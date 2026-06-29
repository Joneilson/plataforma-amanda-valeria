from django.db import models

from apps.common.fields import EncryptedTextField
from apps.common.models import TimeStampedModel


class Conversation(TimeStampedModel):
    """Canal de mensagens entre um paciente e a psicóloga.

    Cada paciente tem exatamente uma conversa (1-1 com a psicóloga).
    """

    patient = models.OneToOneField(
        "patients.Patient", on_delete=models.CASCADE, related_name="conversation"
    )

    class Meta:
        verbose_name = "conversa"
        verbose_name_plural = "conversas"
        ordering = ("-updated_at",)

    def __str__(self):
        return f"Conversa · {self.patient}"


class Message(TimeStampedModel):
    """Mensagem dentro de uma conversa.

    O conteúdo é cifrado em repouso.
    """

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    remetente = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="sent_messages"
    )
    conteudo = EncryptedTextField("conteúdo")
    lida = models.BooleanField(default=False)

    class Meta:
        verbose_name = "mensagem"
        verbose_name_plural = "mensagens"
        ordering = ("created_at",)
        indexes = [
            models.Index(
                fields=["conversation", "created_at"], name="msg_conv_created_idx"
            )
        ]

    def __str__(self):
        return f"{self.remetente} → conversa {self.conversation_id}"
