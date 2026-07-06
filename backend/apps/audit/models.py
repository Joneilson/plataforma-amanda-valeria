from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Trilha de auditoria de eventos sensíveis (LGPD).

    Registra quem fez o quê, quando e de onde. Imutável por design
    (sem updated_at; nunca editar registros existentes).
    """

    class Action(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        LOGIN_FAILED = "LOGIN_FAILED", "Falha de login"
        LOGOUT = "LOGOUT", "Logout"
        REGISTER = "REGISTER", "Cadastro"
        PASSWORD_RESET_REQUEST = "PASSWORD_RESET_REQUEST", "Solicitação de redefinição de senha"
        PASSWORD_RESET = "PASSWORD_RESET", "Redefinição de senha"
        CONSENT_ACCEPTED = "CONSENT_ACCEPTED", "Consentimento aceito"
        DATA_EXPORT = "DATA_EXPORT", "Exportação de dados pessoais"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=40, choices=Action.choices)
    resource = models.CharField(max_length=100, blank=True)
    resource_id = models.CharField(max_length=64, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "registro de auditoria"
        verbose_name_plural = "registros de auditoria"
        indexes = [
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.action} · user={self.user_id} · {self.created_at:%Y-%m-%d %H:%M}"
