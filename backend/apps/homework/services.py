"""Camada de serviços de `homework` — lógica de ESCRITA (regras de negócio)."""
from django.utils import timezone

from .models import Homework


class HomeworkService:
    """Operações de escrita sobre tarefas terapêuticas."""

    @staticmethod
    def create(*, patient, criado_por, titulo: str, descricao: str = "", prazo=None) -> Homework:
        return Homework.objects.create(
            patient=patient,
            criado_por=criado_por,
            titulo=titulo,
            descricao=descricao,
            prazo=prazo,
        )

    @staticmethod
    def update(homework: Homework, **fields) -> Homework:
        for attr, value in fields.items():
            setattr(homework, attr, value)
        homework.save()
        return homework

    @staticmethod
    def set_concluida(homework: Homework, concluida: bool) -> Homework:
        """Marca a tarefa como concluída (ou reabre)."""
        if concluida:
            homework.status = Homework.Status.CONCLUIDA
            homework.concluida_em = timezone.now()
        else:
            homework.status = Homework.Status.PENDENTE
            homework.concluida_em = None
        homework.save(update_fields=["status", "concluida_em", "updated_at"])
        return homework
