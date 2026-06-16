from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import Consent

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "nome", "telefone", "role")
        read_only_fields = ("id", "username", "role")


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password], style={"input_type": "password"}
    )


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consent
        fields = ("id", "tipo", "versao", "ip", "created_at")
        read_only_fields = fields


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Inclui os dados do usuário (e o papel) na resposta do login."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
