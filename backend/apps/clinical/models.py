from django.db import models

from apps.common.fields import EncryptedTextField
from apps.common.models import TimeStampedModel


class PatientNote(TimeStampedModel):
    """Anotação pessoal do paciente.

    O conteúdo é cifrado em repouso. O paciente pode optar por compartilhar
    a anotação com a psicóloga.
    """

    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE, related_name="notes"
    )
    titulo = models.CharField("título", max_length=200, blank=True)
    conteudo = EncryptedTextField("conteúdo")
    compartilhar_com_psicologa = models.BooleanField(
        "compartilhar com a psicóloga", default=False
    )

    class Meta:
        verbose_name = "anotação do paciente"
        verbose_name_plural = "anotações do paciente"
        ordering = ("-updated_at",)
        indexes = [
            models.Index(
                fields=["patient", "-updated_at"], name="note_patient_updated_idx"
            )
        ]

    def __str__(self):
        return f"{self.patient} · {self.titulo or 'sem título'}"
