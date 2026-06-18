"""Camada de selectors de `homework` — lógica de LEITURA (consultas)."""
from .models import Homework


def homeworks_for(user, *, patient_id=None):
    """Tarefas conforme o papel.

    Paciente vê apenas as próprias; psicóloga vê todas (com filtro opcional
    por paciente).
    """
    qs = Homework.objects.select_related("patient__user", "criado_por")
    if user.is_paciente:
        return qs.filter(patient__user=user)
    if patient_id:
        qs = qs.filter(patient_id=patient_id)
    return qs
