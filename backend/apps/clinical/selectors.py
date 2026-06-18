"""Camada de selectors de `clinical` — lógica de LEITURA (consultas)."""
from .models import PatientNote


def notes_for(patient):
    """Anotações de um paciente (todas as dele)."""
    return PatientNote.objects.filter(patient=patient)


def shared_notes():
    """Anotações que os pacientes compartilharam com a psicóloga."""
    return PatientNote.objects.filter(compartilhar_com_psicologa=True).select_related(
        "patient__user"
    )
