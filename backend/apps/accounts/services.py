"""Camada de serviços de `accounts` — lógica de escrita."""
import re
import unicodedata

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.exceptions import ValidationError

from apps.audit.models import AuditLog
from apps.audit.services import log_event

User = get_user_model()


def generate_username(nome: str) -> str:
    """Gera um login no padrão `primeironome.ultimosobrenome`, único."""
    parts = [p for p in nome.strip().split() if p]
    first = parts[0] if parts else "usuario"
    last = parts[-1] if len(parts) > 1 else ""
    base = f"{first}.{last}" if last else first
    base = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode("ascii").lower()
    base = re.sub(r"[^a-z0-9.]", "", base) or "usuario"

    candidate, i = base, 1
    while User.objects.filter(username=candidate).exists():
        i += 1
        candidate = f"{base}{i}"
    return candidate


class PasswordResetService:
    """Fluxo de redefinição de senha via token assinado (sem estado no banco)."""

    @staticmethod
    def request_reset(*, email: str, request=None) -> None:
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if not user or not user.email:
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
