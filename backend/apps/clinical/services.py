"""Camada de serviços de `clinical` — lógica de ESCRITA (regras de negócio)."""
from .models import ClinicalRecord, PatientNote


class ClinicalRecordService:
    """Operações de escrita sobre evoluções clínicas."""

    @staticmethod
    def create(patient, *, conteudo: str, appointment=None) -> ClinicalRecord:
        return ClinicalRecord.objects.create(
            patient=patient,
            conteudo=conteudo,
            appointment=appointment,
        )

    @staticmethod
    def update(record: ClinicalRecord, **fields) -> ClinicalRecord:
        for attr, value in fields.items():
            setattr(record, attr, value)
        record.save()
        return record


class PatientNoteService:
    """Operações de escrita sobre anotações do paciente."""

    @staticmethod
    def create(
        patient, *, conteudo: str, titulo: str = "", compartilhar_com_psicologa: bool = False
    ) -> PatientNote:
        return PatientNote.objects.create(
            patient=patient,
            titulo=titulo,
            conteudo=conteudo,
            compartilhar_com_psicologa=compartilhar_com_psicologa,
        )

    @staticmethod
    def update(note: PatientNote, **fields) -> PatientNote:
        for attr, value in fields.items():
            setattr(note, attr, value)
        note.save()
        return note
