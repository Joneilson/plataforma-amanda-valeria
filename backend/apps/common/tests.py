"""Testes do EncryptedTextField — criptografia em repouso dos dados clínicos."""
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase

from apps.clinical.models import PatientNote
from apps.patients.models import Patient

User = get_user_model()


class EncryptedTextFieldTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username="paciente.teste", password="x", nome="Paciente Teste")
        cls.patient = Patient.objects.create(user=user)

    def test_conteudo_cifrado_no_banco_e_legivel_pela_orm(self):
        segredo = "Conteúdo clínico sigiloso — não pode vazar em texto puro."
        note = PatientNote.objects.create(patient=self.patient, conteudo=segredo)

        # ORM devolve o texto decifrado, transparente para a aplicação.
        note.refresh_from_db()
        self.assertEqual(note.conteudo, segredo)

        # No banco, o valor precisa estar cifrado (prefixo enc:) e sem o texto puro.
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT conteudo FROM clinical_patientnote WHERE id = %s", [note.pk]
            )
            raw = cursor.fetchone()[0]
        self.assertTrue(raw.startswith("enc:"), "conteúdo gravado sem cifra")
        self.assertNotIn("sigiloso", raw)

    def test_dado_legado_sem_cifra_e_retornado_como_esta(self):
        note = PatientNote.objects.create(patient=self.patient, conteudo="tmp")
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE clinical_patientnote SET conteudo = %s WHERE id = %s",
                ["texto legado sem cifra", note.pk],
            )
        note.refresh_from_db()
        self.assertEqual(note.conteudo, "texto legado sem cifra")
