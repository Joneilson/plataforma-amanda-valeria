"""Camada de serviços de `accounts` — lógica de escrita."""
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class AccountService:
    """Operações de criação/alteração de contas."""

    @staticmethod
    @transaction.atomic
    def register_patient(*, email: str, password: str, nome: str, telefone: str = "") -> User:
        """Cria um usuário com papel de paciente.

        O perfil clínico (apps.patients) é criado na Fase 3.
        """
        return User.objects.create_user(
            email=email,
            password=password,
            nome=nome,
            telefone=telefone,
            role=User.Role.PACIENTE,
        )
