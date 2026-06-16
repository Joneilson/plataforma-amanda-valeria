"""Camada de serviços de `patients` — lógica de escrita."""
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Patient

User = get_user_model()


class PatientService:
    """Operações sobre pacientes e suas contas."""

    @staticmethod
    def ensure_profile(user) -> Patient:
        """Garante que um usuário paciente tenha perfil clínico (idempotente)."""
        patient, _ = Patient.objects.get_or_create(user=user)
        return patient

    @staticmethod
    @transaction.atomic
    def create_with_account(*, email: str, nome: str, telefone: str = "", **clinical) -> Patient:
        """Cria a conta do paciente (sem senha utilizável) + o perfil clínico.

        O paciente define a senha depois via "recuperar senha".
        """
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError({"email": "Já existe uma conta com este e-mail."})

        user = User.objects.create_user(
            email=email.lower(),
            password=None,  # senha inutilizável até o paciente redefinir
            nome=nome,
            telefone=telefone,
            role=User.Role.PACIENTE,
        )
        return Patient.objects.create(user=user, **clinical)

    @staticmethod
    def update(patient: Patient, **fields) -> Patient:
        for attr, value in fields.items():
            setattr(patient, attr, value)
        patient.save()
        return patient
