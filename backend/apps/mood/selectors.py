"""Camada de selectors de `mood` — lógica de LEITURA (consultas)."""
from datetime import date, timedelta

from .models import MoodEntry


def mood_entries_for(patient, *, since: date | None = None):
    qs = MoodEntry.objects.filter(patient=patient)
    if since:
        qs = qs.filter(data__gte=since)
    return qs


def entries_for_day(patient, dia: date):
    return MoodEntry.objects.filter(patient=patient, data=dia)


def mood_insights(patient, *, dias: int = 30) -> dict:
    """Série diária e estatísticas dos últimos `dias` dias.

    Cada dia pode ter vários registros; o humor do dia é a média deles.
    Cada ponto traz também os registros ("alterações") do dia, para o tooltip.
    """
    since = date.today() - timedelta(days=dias - 1)
    qs = mood_entries_for(patient, since=since).order_by("data", "created_at")

    por_dia: dict[str, list[MoodEntry]] = {}
    for e in qs:
        por_dia.setdefault(e.data.isoformat(), []).append(e)

    serie = []
    for dia, registros in por_dia.items():
        media_dia = sum(r.nivel for r in registros) / len(registros)
        serie.append(
            {
                "data": dia,
                "media": round(media_dia, 2),
                "registros": [
                    {
                        "hora": r.created_at.isoformat(),
                        "nivel": r.nivel,
                        "nivel_display": r.get_nivel_display(),
                        "emocoes": r.emocoes,
                        "anotacao": r.anotacao,
                    }
                    for r in registros
                ],
            }
        )

    # Média geral = média de como ficou o humor de cada dia.
    media_geral = (
        round(sum(p["media"] for p in serie) / len(serie), 2) if serie else None
    )
    return {
        "serie": serie,
        "media": media_geral,
        "total_registros": qs.count(),
        "dias": dias,
    }
