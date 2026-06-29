import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.messaging.models import Conversation
from apps.messaging.services import MessageService


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket para chat em tempo real entre paciente e psicóloga."""

    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close()
            return

        conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]

        # Verifica se o usuário tem acesso a esta conversa.
        allowed = await self._check_access(user, conversation_id)
        if not allowed:
            await self.close()
            return

        self.conversation_id = conversation_id
        self.group_name = f"chat_{conversation_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        user = self.scope["user"]
        try:
            data = json.loads(text_data)
            conteudo = data.get("conteudo", "").strip()
        except (json.JSONDecodeError, AttributeError):
            return

        if not conteudo:
            return

        msg = await self._save_message(user, conteudo)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "id": msg.id,
                "remetente_id": user.id,
                "remetente_nome": user.nome,
                "remetente_role": user.role,
                "conteudo": conteudo,
                "created_at": msg.created_at.isoformat(),
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "id": event["id"],
                    "remetente": event["remetente_id"],
                    "remetente_nome": event["remetente_nome"],
                    "remetente_role": event["remetente_role"],
                    "conteudo": event["conteudo"],
                    "created_at": event["created_at"],
                }
            )
        )

    @database_sync_to_async
    def _check_access(self, user, conversation_id):
        try:
            conv = Conversation.objects.select_related("patient__user").get(pk=conversation_id)
        except Conversation.DoesNotExist:
            return False
        if user.is_psicologa:
            return True
        if user.is_paciente:
            return conv.patient.user_id == user.id
        return False

    @database_sync_to_async
    def _save_message(self, user, conteudo):
        conv = Conversation.objects.get(pk=self.conversation_id)
        return MessageService.create(conv, user, conteudo)
