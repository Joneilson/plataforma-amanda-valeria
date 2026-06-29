from rest_framework import serializers

from apps.messaging.models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    remetente_nome = serializers.CharField(source="remetente.nome", read_only=True)
    remetente_role = serializers.CharField(source="remetente.role", read_only=True)

    class Meta:
        model = Message
        fields = (
            "id",
            "remetente",
            "remetente_nome",
            "remetente_role",
            "conteudo",
            "lida",
            "created_at",
        )
        read_only_fields = ("id", "remetente", "remetente_nome", "remetente_role", "lida", "created_at")


class ConversationSerializer(serializers.ModelSerializer):
    patient_nome = serializers.CharField(source="patient.user.nome", read_only=True)
    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            "id",
            "patient_id",
            "patient_nome",
            "last_message",
            "unread_count",
            "updated_at",
        )

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if msg:
            return {"conteudo": msg.conteudo[:80], "created_at": msg.created_at}
        return None

    def get_unread_count(self, obj):
        user = self.context["request"].user
        return obj.messages.filter(lida=False).exclude(remetente=user).count()
