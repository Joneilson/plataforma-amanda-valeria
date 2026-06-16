from django.db import models

from apps.common.models import TimeStampedModel


class Modalidade(models.TextChoices):
    ONLINE = "ONLINE", "Online"
    PRESENCIAL = "PRESENCIAL", "Presencial"


class Availability(TimeStampedModel):
    """Grade semanal de disponibilidade da psicóloga."""

    class DiaSemana(models.IntegerChoices):
        SEGUNDA = 0, "Segunda"
        TERCA = 1, "Terça"
        QUARTA = 2, "Quarta"
        QUINTA = 3, "Quinta"
        SEXTA = 4, "Sexta"
        SABADO = 5, "Sábado"
        DOMINGO = 6, "Domingo"

    dia_semana = models.IntegerField(choices=DiaSemana.choices)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    modalidade = models.CharField(
        max_length=12, choices=Modalidade.choices, default=Modalidade.PRESENCIAL
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "disponibilidade"
        verbose_name_plural = "disponibilidades"
        ordering = ("dia_semana", "hora_inicio")

    def __str__(self):
        return f"{self.get_dia_semana_display()} {self.hora_inicio:%H:%M}–{self.hora_fim:%H:%M}"


class Appointment(TimeStampedModel):
    """Sessão/atendimento — núcleo da agenda."""

    class Status(models.TextChoices):
        AGENDADA = "AGENDADA", "Agendada"
        CONFIRMADA = "CONFIRMADA", "Confirmada"
        REALIZADA = "REALIZADA", "Realizada"
        FALTA = "FALTA", "Falta"
        CANCELADA = "CANCELADA", "Cancelada"

    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.PROTECT, related_name="appointments"
    )
    data_hora = models.DateTimeField()
    duracao_min = models.PositiveIntegerField(default=50)
    modalidade = models.CharField(max_length=12, choices=Modalidade.choices)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.AGENDADA)
    valor = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    observacao = models.TextField(blank=True)

    class Meta:
        verbose_name = "atendimento"
        verbose_name_plural = "atendimentos"
        ordering = ("-data_hora",)
        indexes = [models.Index(fields=["status", "data_hora"])]

    def __str__(self):
        return f"{self.patient} · {self.data_hora:%d/%m/%Y %H:%M}"
