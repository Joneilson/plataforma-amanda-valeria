"""Camada de serviços de `mood` — lógica de ESCRITA (regras de negócio)."""
from datetime import date

from .models import MoodEntry


class MoodService:
    """Operações de escrita sobre o humor diário."""

    @staticmethod
    def register(
        patient, *, nivel: int, data: date | None = None, emocoes=None, anotacao: str = ""
    ) -> MoodEntry:
        """Cria um novo registro de humor.

        Atualizar o humor do dia significa registrar de novo: o registro
        anterior é preservado e o humor do dia passa a ser a média dos registros.
        """
        return MoodEntry.objects.create(
            patient=patient,
            data=data or date.today(),
            nivel=nivel,
            emocoes=emocoes or [],
            anotacao=anotacao or "",
        )
