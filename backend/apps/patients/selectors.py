"""Camada de selectors de `patients` — lógica de leitura."""
from .models import Patient


def list_patients(*, status: str | None = None, search: str | None = None):
    qs = Patient.objects.select_related("user")
    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(user__nome__icontains=search)
    return qs


def active_patients_count() -> int:
    return Patient.objects.filter(status=Patient.Status.ATIVO).count()
