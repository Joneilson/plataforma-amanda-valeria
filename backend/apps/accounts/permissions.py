from rest_framework.permissions import BasePermission


class IsPsicologa(BasePermission):
    """Permite acesso apenas à psicóloga (admin)."""

    message = "Acesso restrito à psicóloga."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_psicologa)


class IsPaciente(BasePermission):
    """Permite acesso apenas a pacientes."""

    message = "Acesso restrito a pacientes."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_paciente)
