"""Camada de selectors de `payments` — lógica de LEITURA (consultas)."""
from .models import Payment


def payments_for_patient(patient):
    return Payment.objects.filter(patient=patient).select_related("appointment")


def all_payments():
    return Payment.objects.select_related("patient__user", "appointment").order_by("-created_at")
