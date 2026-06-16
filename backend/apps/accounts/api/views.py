from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.models import Consent
from apps.accounts.services import AccountService, PasswordResetService
from apps.audit.models import AuditLog
from apps.audit.services import log_event

from .serializers import (
    ConsentSerializer,
    CustomTokenObtainPairSerializer,
    LogoutSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
)


def _tokens_for(user) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class LoginView(TokenObtainPairView):
    """Login JWT. Registra o evento de auditoria em caso de sucesso."""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user_data = response.data.get("user", {})
            log_event(
                action=AuditLog.Action.LOGIN,
                request=request,
                resource="user",
                resource_id=user_data.get("id", ""),
            )
        return response


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = AccountService.register_patient(
            email=data["email"],
            password=data["password"],
            nome=data["nome"],
            telefone=data.get("telefone", ""),
            request=request,
        )
        return Response(
            {"user": UserSerializer(user).data, **_tokens_for(user)},
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except TokenError:
            return Response(
                {"detail": "Token inválido."}, status=status.HTTP_400_BAD_REQUEST
            )
        log_event(action=AuditLog.Action.LOGOUT, request=request, user=request.user)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PasswordResetService.request_reset(
            email=serializer.validated_data["email"], request=request
        )
        # Resposta neutra: não revela se o e-mail existe.
        return Response(
            {"detail": "Se o e-mail estiver cadastrado, enviaremos as instruções."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        PasswordResetService.confirm_reset(
            uidb64=data["uid"],
            token=data["token"],
            new_password=data["new_password"],
            request=request,
        )
        return Response({"detail": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)


class MeView(APIView):
    """Retorna os dados do usuário autenticado."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ConsentListView(ListAPIView):
    serializer_class = ConsentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Consent.objects.filter(user=self.request.user)
