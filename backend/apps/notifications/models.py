from django.db import models

from apps.common.models import TimeStampedModel


class SessionReminder(TimeStampedModel):
    """Marca que o lembrete de 24h do atendimento já foi processado.

    Existência do registro = lembrete tratado (enviado ou paciente sem e-mail).
    Garante idempotência: a task horária nunca envia duas vezes.
    """

    appointment = models.OneToOneField(
        "scheduling.Appointment", on_delete=models.CASCADE, related_name="reminder"
    )
    email_enviado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "lembrete de sessão"
        verbose_name_plural = "lembretes de sessão"

    def __str__(self):
        return f"Lembrete · atendimento {self.appointment_id}"
