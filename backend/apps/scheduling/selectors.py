"""Camada de selectors de `scheduling` — lógica de leitura."""
from django.db.models import Sum
from django.utils import timezone

from apps.patients.models import Patient

from .models import Appointment


def appointments_for(user):
    """Atendimentos visíveis ao usuário, conforme o papel."""
    qs = Appointment.objects.select_related("patient__user")
    if user.is_psicologa:
        return qs
    return qs.filter(patient__user=user)


def next_appointment_for_patient(patient: Patient):
    return (
        Appointment.objects.filter(
            patient=patient,
            data_hora__gte=timezone.now(),
            status__in=[Appointment.Status.AGENDADA, Appointment.Status.CONFIRMADA],
        )
        .order_by("data_hora")
        .first()
    )


def admin_metrics() -> dict:
    realizadas = Appointment.objects.filter(status=Appointment.Status.REALIZADA)
    minutos = realizadas.aggregate(total=Sum("duracao_min"))["total"] or 0
    now = timezone.now()

    return {
        "atendimentos_realizados": realizadas.count(),
        "horas_atendidas": round(minutos / 60, 1),
        "online": realizadas.filter(modalidade="ONLINE").count(),
        "presencial": realizadas.filter(modalidade="PRESENCIAL").count(),
        "faltas": Appointment.objects.filter(status=Appointment.Status.FALTA).count(),
        "pacientes_ativos": Patient.objects.filter(status=Patient.Status.ATIVO).count(),
        "proximos_7_dias": Appointment.objects.filter(
            data_hora__range=(now, now + timezone.timedelta(days=7)),
            status__in=[Appointment.Status.AGENDADA, Appointment.Status.CONFIRMADA],
        ).count(),
    }
