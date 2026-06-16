from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import TimeStampedModel

from .managers import UserManager


class User(AbstractUser):
    """Usuário do sistema. Autenticação por e-mail; papel define o acesso."""

    class Role(models.TextChoices):
        PACIENTE = "PACIENTE", "Paciente"
        PSICOLOGA = "PSICOLOGA", "Psicóloga"

    # Removemos username em favor do e-mail.
    username = None

    email = models.EmailField("e-mail", unique=True)
    nome = models.CharField("nome completo", max_length=150)
    telefone = models.CharField("telefone", max_length=20, blank=True)
    role = models.CharField(
        "papel", max_length=20, choices=Role.choices, default=Role.PACIENTE
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    objects = UserManager()

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"

    def __str__(self):
        return f"{self.nome} <{self.email}>"

    @property
    def is_psicologa(self) -> bool:
        return self.role == self.Role.PSICOLOGA

    @property
    def is_paciente(self) -> bool:
        return self.role == self.Role.PACIENTE


class Consent(TimeStampedModel):
    """Registro de consentimento aceito pelo usuário (LGPD / CFP).

    Versionado: cada versão dos termos gera um aceite próprio, com data e IP.
    """

    class Type(models.TextChoices):
        TERMS = "TERMOS_USO", "Termos de uso"
        PRIVACY = "PRIVACIDADE", "Política de privacidade (LGPD)"
        TELEHEALTH = "TELEATENDIMENTO", "Consentimento de teleatendimento (CFP)"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consents"
    )
    tipo = models.CharField(max_length=30, choices=Type.choices)
    versao = models.CharField(max_length=20, default="1.0")
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "consentimento"
        verbose_name_plural = "consentimentos"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tipo", "versao"], name="unique_consent_per_version"
            )
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} v{self.versao} · {self.user_id}"
