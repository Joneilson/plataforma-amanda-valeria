from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Homework(TimeStampedModel):
    """Tarefa terapêutica: a psicóloga cria, o paciente conclui."""

    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        CONCLUIDA = "CONCLUIDA", "Concluída"

    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE, related_name="homeworks"
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    titulo = models.CharField("título", max_length=200)
    descricao = models.TextField("descrição", blank=True)
    prazo = models.DateField("prazo", null=True, blank=True)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDENTE
    )
    concluida_em = models.DateTimeField("concluída em", null=True, blank=True)

    class Meta:
        verbose_name = "tarefa terapêutica"
        verbose_name_plural = "tarefas terapêuticas"
        ordering = ("status", "prazo", "-created_at")
        indexes = [models.Index(fields=["patient", "status"], name="hw_patient_status_idx")]

    def __str__(self):
        return f"{self.patient} · {self.titulo} ({self.get_status_display()})"
