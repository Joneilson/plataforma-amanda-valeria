"""Camada de serviços de `patients` — lógica de escrita."""
from django.contrib.auth import get_user_model
from django.db import transaction

from apps.accounts.models import Consent
from apps.accounts.services import generate_username
from apps.audit.models import AuditLog
from apps.audit.services import get_client_ip, log_event

from .models import Patient

User = get_user_model()


class PatientService:
    """Operações sobre pacientes e suas contas."""

    @staticmethod
    def ensure_profile(user) -> Patient:
        patient, _ = Patient.objects.get_or_create(user=user)
        return patient

    @staticmethod
    @transaction.atomic
    def create_with_account(
        *, nome: str, password: str, email: str | None = None, telefone: str = "", request=None, **clinical
    ) -> Patient:
        """Cria a conta do paciente (login `nome.sobrenome`) + perfil clínico.

        A psicóloga define a senha inicial e o login é gerado automaticamente.
        """
        user = User.objects.create_user(
            username=generate_username(nome),
            password=password,
            nome=nome,
            email=(email or None),
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

        patient = Patient.objects.create(user=user, **clinical)
        log_event(
            action=AuditLog.Action.REGISTER,
            request=request,
            user=user,
            resource="patient",
            resource_id=patient.id,
        )
        return patient

    @staticmethod
    def update(patient: Patient, **fields) -> Patient:
        for attr, value in fields.items():
            setattr(patient, attr, value)
        patient.save()
        return patient
