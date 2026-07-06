"""Testes de isolamento do prontuário e das anotações — quem vê o quê."""
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from apps.clinical.models import ClinicalRecord, PatientNote
from apps.patients.models import Patient

User = get_user_model()


class ClinicalAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.psicologa = User.objects.create_user(
            username="amanda", password="x", nome="Amanda Valeria", role=User.Role.PSICOLOGA
        )
        user_a = User.objects.create_user(username="ana.silva", password="x", nome="Ana Silva")
        user_b = User.objects.create_user(username="bruno.souza", password="x", nome="Bruno Souza")
        cls.paciente_a = Patient.objects.create(user=user_a)
        cls.paciente_b = Patient.objects.create(user=user_b)

        cls.record_a = ClinicalRecord.objects.create(
            patient=cls.paciente_a, conteudo="Evolução clínica da Ana."
        )
        cls.nota_privada_a = PatientNote.objects.create(
            patient=cls.paciente_a, titulo="privada", conteudo="Só minha."
        )
        cls.nota_compartilhada_a = PatientNote.objects.create(
            patient=cls.paciente_a,
            titulo="compartilhada",
            conteudo="Quero falar disso na sessão.",
            compartilhar_com_psicologa=True,
        )

    def setUp(self):
        cache.clear()
        self.client = APIClient()

    # ---- Prontuário (ClinicalRecord) ----

    def test_paciente_nao_acessa_prontuario(self):
        self.client.force_authenticate(self.paciente_a.user)
        self.assertEqual(self.client.get("/api/clinical-records").status_code, 403)
        self.assertEqual(
            self.client.get(f"/api/clinical-records/{self.record_a.pk}").status_code, 403
        )

    def test_psicologa_acessa_prontuario(self):
        self.client.force_authenticate(self.psicologa)
        resp = self.client.get(f"/api/clinical-records?patient={self.paciente_a.pk}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["conteudo"], "Evolução clínica da Ana.")

    # ---- Anotações pessoais (PatientNote) ----

    def test_paciente_ve_apenas_as_proprias_notas(self):
        self.client.force_authenticate(self.paciente_b.user)
        resp = self.client.get("/api/notes")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)

    def test_paciente_nao_acessa_nota_de_outro_por_id(self):
        self.client.force_authenticate(self.paciente_b.user)
        resp = self.client.get(f"/api/notes/{self.nota_privada_a.pk}")
        self.assertEqual(resp.status_code, 404)

    def test_psicologa_nao_acessa_endpoint_de_notas_do_paciente(self):
        self.client.force_authenticate(self.psicologa)
        self.assertEqual(self.client.get("/api/notes").status_code, 403)

    def test_psicologa_ve_somente_notas_compartilhadas(self):
        self.client.force_authenticate(self.psicologa)
        resp = self.client.get("/api/shared-notes")
        self.assertEqual(resp.status_code, 200)
        titulos = [n["titulo"] for n in resp.data]
        self.assertIn("compartilhada", titulos)
        self.assertNotIn("privada", titulos)
