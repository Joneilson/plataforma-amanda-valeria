"""Camada de selectors de `clinical` — lógica de LEITURA (consultas)."""
from .models import ClinicalRecord, PatientNote


def records_for(patient):
    """Evoluções clínicas de um paciente, ordenadas das mais recentes."""
    return ClinicalRecord.objects.filter(patient=patient).select_related("appointment")


def notes_for(patient):
    """Anotações de um paciente (todas as dele)."""
    return PatientNote.objects.filter(patient=patient)


def shared_notes():
    """Anotações que os pacientes compartilharam com a psicóloga."""
    return PatientNote.objects.filter(compartilhar_com_psicologa=True).select_related(
        "patient__user"
    )
