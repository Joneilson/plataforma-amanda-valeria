from django.contrib.auth.models import AbstractUser
from django.db import models

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
