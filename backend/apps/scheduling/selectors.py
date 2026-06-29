"""Camada de selectors de `scheduling` — lógica de leitura."""
from django.db.models import Sum
from django.utils import timezone

from apps.patients.models import Patient

from .models import Appointment


def _financial_metrics() -> dict:
    from apps.payments.models import Payment

    now = timezone.now()
    mes_inicio = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    faturamento_mes = (
        Payment.objects.filter(status=Payment.Status.PAGO, pago_em__gte=mes_inicio)
        .aggregate(total=Sum("valor"))["total"]
        or 0
    )
    contas_a_receber = (
        Payment.objects.filter(status=Payment.Status.PENDENTE)
        .aggregate(total=Sum("valor"))["total"]
        or 0
    )
    pagamentos_pendentes = Payment.objects.filter(status=Payment.Status.PENDENTE).count()

    return {
        "faturamento_mes": float(faturamento_mes),
        "contas_a_receber": float(contas_a_receber),
        "pagamentos_pendentes": pagamentos_pendentes,
    }


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

    metrics = {
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
    metrics.update(_financial_metrics())
    return metrics
