"""Camada de selectors de `video` — lógica de LEITURA (consultas)."""
from .models import VideoRoom


def room_for_appointment(appointment_id: int) -> VideoRoom | None:
    return VideoRoom.objects.filter(appointment_id=appointment_id).first()
