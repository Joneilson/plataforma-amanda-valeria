from django.db import models

from apps.common.models import TimeStampedModel


class Payment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        PAGO = "PAGO", "Pago"
        FALHOU = "FALHOU", "Falhou"
        ESTORNADO = "ESTORNADO", "Estornado"

    class Metodo(models.TextChoices):
        PIX = "PIX", "Pix"
        CARTAO = "CARTAO", "Cartão"
        MANUAL = "MANUAL", "Manual (externo)"

    appointment = models.OneToOneField(
        "scheduling.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment",
    )
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.PROTECT, related_name="payments"
    )
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDENTE)
    metodo = models.CharField(max_length=12, choices=Metodo.choices, default=Metodo.PIX)
    provider = models.CharField(max_length=20, default="mercadopago")
    provider_payment_id = models.CharField(max_length=100, blank=True)
    qr_code = models.TextField(blank=True)
    qr_code_base64 = models.TextField(blank=True)
    link_pagamento = models.URLField(max_length=500, blank=True)
    pago_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "pagamento"
        verbose_name_plural = "pagamentos"
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["patient", "-created_at"], name="pay_patient_created_idx")]

    def __str__(self):
        return f"Pagamento #{self.pk} — {self.patient} [{self.status}]"
