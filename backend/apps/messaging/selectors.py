"""Camada de selectors de `messaging` — lógica de LEITURA (consultas)."""
from .models import Conversation, Message


def all_conversations():
    """Todas as conversas, ordenadas pela mais recente atividade."""
    return Conversation.objects.select_related("patient__user").order_by("-updated_at")


def messages_for(conversation: Conversation, limit: int = 100):
    """Últimas `limit` mensagens de uma conversa, em ordem cronológica."""
    return (
        Message.objects.filter(conversation=conversation)
        .select_related("remetente")
        .order_by("created_at")[:limit]
    )


def unread_count(conversation: Conversation, reader) -> int:
    return Message.objects.filter(
        conversation=conversation, lida=False
    ).exclude(remetente=reader).count()
