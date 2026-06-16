from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel


class Patient(TimeStampedModel):
    """Perfil clínico do paciente (1–1 com a conta de usuário).

    Campos sensíveis (queixa, contato de emergência) serão criptografados
    em repouso na Fase 8 (hardening).
    """

    class Status(models.TextChoices):
        ATIVO = "ATIVO", "Ativo"
        INATIVO = "INATIVO", "Inativo"
        ALTA = "ALTA", "Alta"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient"
    )
    data_nascimento = models.DateField("data de nascimento", null=True, blank=True)
    genero = models.CharField("gênero", max_length=40, blank=True)
    queixa_principal = models.TextField("queixa principal", blank=True)
    contato_emergencia_nome = models.CharField(max_length=150, blank=True)
    contato_emergencia_telefone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ATIVO)
    inicio_tratamento = models.DateField("início do tratamento", default=timezone.localdate)
    valor_sessao = models.DecimalField(
        "valor da sessão", max_digits=8, decimal_places=2, null=True, blank=True
    )

    class Meta:
        verbose_name = "paciente"
        verbose_name_plural = "pacientes"
        ordering = ("user__nome",)

    def __str__(self):
        return self.user.nome
