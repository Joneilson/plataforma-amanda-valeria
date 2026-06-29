"""Camada de serviços de `messaging` — lógica de ESCRITA (regras de negócio)."""
from .models import Conversation, Message


class ConversationService:
    @staticmethod
    def get_or_create(patient) -> Conversation:
        conversation, _ = Conversation.objects.get_or_create(patient=patient)
        return conversation


class MessageService:
    @staticmethod
    def create(conversation: Conversation, remetente, conteudo: str) -> Message:
        msg = Message.objects.create(
            conversation=conversation,
            remetente=remetente,
            conteudo=conteudo,
        )
        # Atualiza timestamp da conversa para ordenação por atividade recente.
        Conversation.objects.filter(pk=conversation.pk).update(
            updated_at=msg.created_at
        )
        return msg

    @staticmethod
    def mark_as_read(conversation: Conversation, reader) -> int:
        """Marca como lidas todas as mensagens NÃO enviadas pelo leitor."""
        return Message.objects.filter(
            conversation=conversation, lida=False
        ).exclude(remetente=reader).update(lida=True)
