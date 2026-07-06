"""Camada de serviços de `accounts` — lógica de escrita."""
import re
import unicodedata

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.exceptions import ValidationError

from apps.accounts.models import Consent
from apps.audit.models import AuditLog
from apps.audit.services import get_client_ip, log_event

User = get_user_model()

# Versões vigentes dos termos. Ao publicar uma nova versão de um documento,
# atualize aqui — os pacientes serão solicitados a aceitar novamente.
CURRENT_CONSENT_VERSIONS = {
    Consent.Type.TERMS: "1.0",
    Consent.Type.PRIVACY: "1.0",
    Consent.Type.TELEHEALTH: "1.0",
}


class ConsentService:
    """Aceite e pendências de consentimento (LGPD art. 7º/11 + CFP 09/2024)."""

    @staticmethod
    def pending_for(user) -> list[str]:
        """Tipos de consentimento exigidos do usuário e ainda não aceitos na versão vigente."""
        if not user.is_paciente:
            return []
        accepted = set(Consent.objects.filter(user=user).values_list("tipo", "versao"))
        return [
            tipo
            for tipo, versao in CURRENT_CONSENT_VERSIONS.items()
            if (tipo, versao) not in accepted
        ]

    @staticmethod
    def accept(*, user, tipo: str, request=None) -> Consent:
        if tipo not in CURRENT_CONSENT_VERSIONS:
            raise ValidationError({"tipo": "Tipo de consentimento inválido."})
        versao = CURRENT_CONSENT_VERSIONS[tipo]
        consent, created = Consent.objects.get_or_create(
            user=user,
            tipo=tipo,
            versao=versao,
            defaults={"ip": get_client_ip(request)},
        )
        if created:
            log_event(
                action=AuditLog.Action.CONSENT_ACCEPTED,
                request=request,
                user=user,
                resource="consent",
                resource_id=consent.pk,
                metadata={"tipo": tipo, "versao": versao},
            )
        return consent


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


class DataExportService:
    """Exportação dos dados pessoais do paciente (LGPD art. 18, portabilidade).

    Não inclui o prontuário (evolução clínica): é registro profissional da
    psicóloga (CFP 01/2009) e pode ser solicitado formalmente à parte.
    """

    @staticmethod
    def export_for(user, request=None) -> dict:
        from apps.homework.models import Homework
        from apps.messaging.models import Message
        from apps.mood.models import MoodEntry
        from apps.patients.models import Patient

        data: dict = {
            "gerado_em": timezone.now().isoformat(),
            "usuario": {
                "nome": user.nome,
                "username": user.username,
                "email": user.email,
                "telefone": user.telefone,
                "cadastrado_em": user.date_joined.isoformat(),
            },
            "consentimentos": [
                {
                    "tipo": c.get_tipo_display(),
                    "versao": c.versao,
                    "aceito_em": c.created_at.isoformat(),
                }
                for c in user.consents.all()
            ],
        }

        patient = Patient.objects.filter(user=user).first()
        if patient:
            data["perfil"] = {
                "data_nascimento": patient.data_nascimento.isoformat() if patient.data_nascimento else None,
                "genero": patient.genero,
                "status": patient.get_status_display(),
                "inicio_tratamento": patient.inicio_tratamento.isoformat(),
                "contato_emergencia_nome": patient.contato_emergencia_nome,
                "contato_emergencia_telefone": patient.contato_emergencia_telefone,
            }
            data["atendimentos"] = [
                {
                    "data_hora": a.data_hora.isoformat(),
                    "duracao_min": a.duracao_min,
                    "modalidade": a.modalidade,
                    "status": a.get_status_display(),
                    "valor": str(a.valor) if a.valor is not None else None,
                }
                for a in patient.appointments.all()
            ]
            data["pagamentos"] = [
                {
                    "valor": str(p.valor),
                    "status": p.get_status_display(),
                    "metodo": p.get_metodo_display(),
                    "criado_em": p.created_at.isoformat(),
                    "pago_em": p.pago_em.isoformat() if p.pago_em else None,
                }
                for p in patient.payments.all()
            ]
            data["registros_de_humor"] = [
                {
                    "data": m.data.isoformat(),
                    "nivel": m.get_nivel_display(),
                    "emocoes": m.emocoes,
                    "anotacao": m.anotacao,
                }
                for m in MoodEntry.objects.filter(patient=patient)
            ]
            data["anotacoes_pessoais"] = [
                {
                    "titulo": n.titulo,
                    "conteudo": n.conteudo,
                    "compartilhada_com_psicologa": n.compartilhar_com_psicologa,
                    "criada_em": n.created_at.isoformat(),
                }
                for n in patient.notes.all()
            ]
            data["tarefas_terapeuticas"] = [
                {
                    "titulo": h.titulo,
                    "descricao": h.descricao,
                    "prazo": h.prazo.isoformat() if h.prazo else None,
                    "status": h.get_status_display(),
                    "concluida_em": h.concluida_em.isoformat() if h.concluida_em else None,
                }
                for h in Homework.objects.filter(patient=patient)
            ]
            conversation = getattr(patient, "conversation", None)
            data["mensagens"] = [
                {
                    "remetente": m.remetente.nome,
                    "conteudo": m.conteudo,
                    "enviada_em": m.created_at.isoformat(),
                }
                for m in Message.objects.filter(conversation=conversation).select_related("remetente")
            ] if conversation else []

        log_event(
            action=AuditLog.Action.DATA_EXPORT,
            request=request,
            user=user,
            resource="user",
            resource_id=user.pk,
        )
        return data
