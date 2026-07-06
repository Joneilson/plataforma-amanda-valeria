"""Testes de pagamentos — BRCode PIX, idempotência e isolamento entre pacientes."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.patients.models import Patient
from apps.payments.models import Payment
from apps.payments.services import PixService, _build_pix_payload, _crc16
from apps.scheduling.models import Appointment

User = get_user_model()


def _make_paciente(username: str, nome: str) -> Patient:
    user = User.objects.create_user(username=username, password="x", nome=nome)
    return Patient.objects.create(user=user, valor_sessao=Decimal("150.00"))


def _make_appointment(patient: Patient) -> Appointment:
    return Appointment.objects.create(
        patient=patient, data_hora=timezone.now(), modalidade="ONLINE"
    )


class PixPayloadTests(TestCase):
    def test_crc16_check_value_canonico(self):
        # Vetor de teste padrão do CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF),
        # o algoritmo exigido pelo BRCode do BACEN: "123456789" -> 0x29B1.
        self.assertEqual(_crc16("123456789"), "29B1")

    def test_payload_estrutura_emv(self):
        payload = _build_pix_payload(
            "87991730248", "Amanda Valeria", "Garanhuns", Decimal("150.00"), "AMN0000000001"
        )
        self.assertTrue(payload.startswith("000201"))
        self.assertIn("BR.GOV.BCB.PIX", payload)
        self.assertIn("87991730248", payload)
        self.assertIn("5303986", payload)      # moeda BRL
        self.assertIn("54" + "06" + "150.00", payload)  # valor
        # CRC final consistente com o próprio conteúdo.
        self.assertEqual(payload[-4:], _crc16(payload[:-4]))

    def test_nome_e_cidade_truncados_nos_limites_emv(self):
        payload = _build_pix_payload(
            "chave@pix.com", "N" * 40, "C" * 30, Decimal("1.00"), "TX1"
        )
        self.assertIn("59" + "25" + "N" * 25, payload)  # nome máx. 25
        self.assertIn("60" + "15" + "C" * 15, payload)  # cidade máx. 15
        self.assertEqual(payload[-4:], _crc16(payload[:-4]))


@override_settings(PIX_KEY="87991730248")
class PixServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.patient = _make_paciente("ana.silva", "Ana Silva")
        cls.apt = _make_appointment(cls.patient)

    def test_create_pix_idempotente(self):
        p1 = PixService.create_pix(self.apt, self.patient)
        p2 = PixService.create_pix(self.apt, self.patient)
        self.assertEqual(p1.pk, p2.pk)

    def test_valor_vem_do_appointment_ou_do_paciente(self):
        payment = PixService.create_pix(self.apt, self.patient)
        self.assertEqual(payment.valor, Decimal("150.00"))  # valor_sessao do paciente


class PaymentAPIPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.psicologa = User.objects.create_user(
            username="amanda", password="x", nome="Amanda Valeria", role=User.Role.PSICOLOGA
        )
        cls.paciente_a = _make_paciente("ana.silva", "Ana Silva")
        cls.paciente_b = _make_paciente("bruno.souza", "Bruno Souza")
        cls.apt_a = _make_appointment(cls.paciente_a)

    def setUp(self):
        cache.clear()  # zera contadores de throttle entre testes
        self.client = APIClient()

    @override_settings(PIX_KEY="87991730248")
    def test_paciente_nao_gera_cobranca_de_atendimento_alheio(self):
        self.client.force_authenticate(self.paciente_b.user)
        resp = self.client.post(
            "/api/payments/checkout", {"appointment_id": self.apt_a.pk}, format="json"
        )
        self.assertEqual(resp.status_code, 404)

    @override_settings(PIX_KEY="87991730248")
    def test_paciente_gera_cobranca_do_proprio_atendimento(self):
        self.client.force_authenticate(self.paciente_a.user)
        resp = self.client.post(
            "/api/payments/checkout", {"appointment_id": self.apt_a.pk}, format="json"
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.data["qr_code"].startswith("000201"))

    @override_settings(PIX_KEY="")
    def test_checkout_sem_pix_key_retorna_503(self):
        self.client.force_authenticate(self.paciente_a.user)
        resp = self.client.post(
            "/api/payments/checkout", {"appointment_id": self.apt_a.pk}, format="json"
        )
        self.assertEqual(resp.status_code, 503)

    def test_psicologa_nao_usa_checkout_de_paciente(self):
        self.client.force_authenticate(self.psicologa)
        resp = self.client.post(
            "/api/payments/checkout", {"appointment_id": self.apt_a.pk}, format="json"
        )
        self.assertEqual(resp.status_code, 403)

    def test_paciente_nao_lista_todos_os_pagamentos(self):
        self.client.force_authenticate(self.paciente_a.user)
        self.assertEqual(self.client.get("/api/payments").status_code, 403)

    def test_paciente_nao_marca_como_pago(self):
        with override_settings(PIX_KEY="87991730248"):
            payment = PixService.create_pix(self.apt_a, self.paciente_a)
        self.client.force_authenticate(self.paciente_a.user)
        resp = self.client.post(f"/api/payments/{payment.pk}/marcar-pago")
        self.assertEqual(resp.status_code, 403)


class MonthlyReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.utils import timezone as tz

        cls.psicologa = User.objects.create_user(
            username="amanda", password="x", nome="Amanda Valeria", role=User.Role.PSICOLOGA
        )
        cls.paciente = _make_paciente("ana.silva", "Ana Silva")
        apt = _make_appointment(cls.paciente)
        payment = Payment.objects.create(
            appointment=apt,
            patient=cls.paciente,
            valor=Decimal("150.00"),
            status=Payment.Status.PAGO,
            pago_em=tz.now(),
        )
        cls.payment = payment

    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_psicologa_ve_resumo_do_mes(self):
        from django.utils import timezone as tz

        hoje = tz.localdate()
        self.client.force_authenticate(self.psicologa)
        resp = self.client.get(f"/api/reports/monthly?ano={hoje.year}&mes={hoje.month}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["atendimentos"]["total"], 1)
        self.assertEqual(resp.data["financeiro"]["recebido_no_mes"], "150.00")
        self.assertEqual(resp.data["por_paciente"][0]["paciente"], "Ana Silva")

    def test_paciente_nao_acessa_relatorio(self):
        self.client.force_authenticate(self.paciente.user)
        resp = self.client.get("/api/reports/monthly")
        self.assertEqual(resp.status_code, 403)

    def test_mes_invalido_retorna_400(self):
        self.client.force_authenticate(self.psicologa)
        resp = self.client.get("/api/reports/monthly?ano=2026&mes=13")
        self.assertEqual(resp.status_code, 400)
