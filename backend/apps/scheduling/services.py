"""Camada de serviços de `scheduling` — lógica de escrita."""
from .models import Appointment


class AppointmentService:
    """Operações de escrita sobre atendimentos.

    A criação/edição simples é feita pelo serializer; aqui ficam as
    transições de estado e regras que evoluem nas próximas fases
    (ex.: provisionar sala de vídeo, gerar cobrança).
    """

    VALID_STATUS = set(Appointment.Status.values)

    @staticmethod
    def set_status(appointment: Appointment, status: str) -> Appointment:
        if status not in AppointmentService.VALID_STATUS:
            raise ValueError(f"Status inválido: {status}")
        appointment.status = status
        appointment.save(update_fields=["status", "updated_at"])
        return appointment
