"""Camada de selectors de `accounts` — lógica de leitura."""
from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_by_email(email: str) -> User | None:
    return User.objects.filter(email__iexact=email).first()
