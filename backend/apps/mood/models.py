from django.db import models

from apps.common.fields import EncryptedTextField
from apps.common.models import TimeStampedModel


class MoodEntry(TimeStampedModel):
    """Registro de humor do paciente.

    Pode haver vários registros no mesmo dia: cada atualização cria um novo
    registro (preserva os anteriores). O humor do dia é a média desses registros.
    """

    class Nivel(models.IntegerChoices):
        MUITO_RUIM = 1, "Muito ruim"
        RUIM = 2, "Ruim"
        NEUTRO = 3, "Neutro"
        BOM = 4, "Bom"
        OTIMO = 5, "Ótimo"

    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE, related_name="mood_entries"
    )
    data = models.DateField("data")
    nivel = models.PositiveSmallIntegerField("nível", choices=Nivel.choices)
    emocoes = models.JSONField("emoções", default=list, blank=True)
    anotacao = EncryptedTextField("anotação", blank=True)

    class Meta:
        verbose_name = "registro de humor"
        verbose_name_plural = "registros de humor"
        ordering = ("-data", "-created_at")
        indexes = [models.Index(fields=["patient", "data"], name="mood_patient_data_idx")]

    def __str__(self):
        return f"{self.patient} · {self.data:%d/%m/%Y} · {self.get_nivel_display()}"
