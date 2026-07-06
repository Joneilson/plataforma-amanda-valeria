"""Testes do lembrete de sessão 24h antes."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from apps.notifications.models import SessionReminder
from apps.notifications.tasks import enviar_lembretes_de_sessao
from apps.patients.models import Patient
from apps.scheduling.models import Appointment

User = get_user_model()


def _paciente(username: str, email: str = "") -> Patient:
    user = User.objects.create_user(
        username=username, password="x", nome=username.title(), email=email or None
    )
    return Patient.objects.create(user=user)


def _apt(patient: Patient, horas: int, status=Appointment.Status.AGENDADA) -> Appointment:
    return Appointment.objects.create(
        patient=patient,
        data_hora=timezone.now() + timedelta(hours=horas),
        modalidade="ONLINE",
        status=status,
    )


class SessionReminderTaskTests(TestCase):
    def test_envia_para_sessao_nas_proximas_24h(self):
        apt = _apt(_paciente("ana.silva", "ana@exemplo.com"), horas=20)
        enviados = enviar_lembretes_de_sessao()
        self.assertEqual(enviados, 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("sessão", mail.outbox[0].subject)
        self.assertTrue(SessionReminder.objects.filter(appointment=apt, email_enviado=True).exists())

    def test_nao_reenvia_na_segunda_execucao(self):
        _apt(_paciente("ana.silva", "ana@exemplo.com"), horas=20)
        enviar_lembretes_de_sessao()
        enviados = enviar_lembretes_de_sessao()
        self.assertEqual(enviados, 0)
        self.assertEqual(len(mail.outbox), 1)

    def test_ignora_sessao_alem_de_24h_e_canceladas(self):
        _apt(_paciente("ana.silva", "ana@exemplo.com"), horas=48)
        _apt(_paciente("bruno.souza", "bruno@exemplo.com"), horas=10, status=Appointment.Status.CANCELADA)
        enviados = enviar_lembretes_de_sessao()
        self.assertEqual(enviados, 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_paciente_sem_email_marca_processado_sem_enviar(self):
        apt = _apt(_paciente("caio.lima"), horas=20)
        enviados = enviar_lembretes_de_sessao()
        self.assertEqual(enviados, 0)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(SessionReminder.objects.filter(appointment=apt, email_enviado=False).exists())
