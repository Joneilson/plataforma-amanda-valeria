"""Camada de serviços de `accounts` — lógica de escrita."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.exceptions import ValidationError

from apps.audit.models import AuditLog
from apps.audit.services import get_client_ip, log_event

from .models import Consent

User = get_user_model()


class AccountService:
    """Operações de criação/alteração de contas."""

    @staticmethod
    @transaction.atomic
    def register_patient(*, email, password, nome, telefone="", request=None) -> User:
        """Cria um usuário paciente e registra os consentimentos obrigatórios.

        O perfil clínico (apps.patients) é criado na Fase 3.
        """
        user = User.objects.create_user(
            email=email,
            password=password,
            nome=nome,
            telefone=telefone,
            role=User.Role.PACIENTE,
        )

        ip = get_client_ip(request)
        Consent.objects.bulk_create(
            [
                Consent(user=user, tipo=tipo, ip=ip)
                for tipo in (Consent.Type.TERMS, Consent.Type.PRIVACY)
            ]
        )

        # Cria o perfil clínico do paciente (import tardio evita acoplamento no carregamento).
        from apps.patients.services import PatientService

        PatientService.ensure_profile(user)

        log_event(action=AuditLog.Action.REGISTER, request=request, user=user)
        return user


class PasswordResetService:
    """Fluxo de redefinição de senha via token assinado (sem estado no banco)."""

    @staticmethod
    def request_reset(*, email: str, request=None) -> None:
        """Envia o link de redefinição. Responde igual exista ou não a conta
        (não revela se o e-mail está cadastrado)."""
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if not user:
            return

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        link = f"{settings.FRONTEND_URL}/redefinir-senha?uid={uid}&token={token}"

        send_mail(
            subject="Redefinição de senha",
            message=(
                f"Olá, {user.nome}.\n\n"
                f"Para redefinir sua senha, acesse:\n{link}\n\n"
                "Se você não solicitou, ignore este e-mail."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        log_event(action=AuditLog.Action.PASSWORD_RESET_REQUEST, request=request, user=user)

    @staticmethod
    @transaction.atomic
    def confirm_reset(*, uidb64: str, token: str, new_password: str, request=None) -> User:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise ValidationError("Link inválido.")

        if not default_token_generator.check_token(user, token):
            raise ValidationError("Link inválido ou expirado.")

        user.set_password(new_password)
        user.save(update_fields=["password"])
        log_event(action=AuditLog.Action.PASSWORD_RESET, request=request, user=user)
        return user
