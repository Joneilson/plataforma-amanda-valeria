"""Tasks Celery de notificações — lembrete de sessão 24h antes."""
import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def enviar_lembretes_de_sessao() -> int:
    """Envia lembrete por e-mail para sessões nas próximas 24h.

    Roda de hora em hora (Celery Beat). Idempotente via SessionReminder.
    Retorna o número de e-mails enviados.
    """
    from apps.notifications.models import SessionReminder
    from apps.scheduling.models import Appointment

    now = timezone.now()
    proximos = (
        Appointment.objects.filter(
            data_hora__gt=now,
            data_hora__lte=now + timedelta(hours=24),
            status__in=[Appointment.Status.AGENDADA, Appointment.Status.CONFIRMADA],
            reminder__isnull=True,
        )
        .select_related("patient__user")
    )

    enviados = 0
    for apt in proximos:
        user = apt.patient.user
        email_enviado = False
        if user.email:
            local = timezone.localtime(apt.data_hora)
            try:
                send_mail(
                    subject="Lembrete: sua sessão é amanhã",
                    message=(
                        f"Olá, {user.nome}.\n\n"
                        f"Você tem uma sessão {apt.get_modalidade_display().lower()} agendada para "
                        f"{local:%d/%m/%Y} às {local:%H:%M}.\n\n"
                        + (
                            f"Acesse a plataforma para entrar na sala: {settings.FRONTEND_URL}\n\n"
                            if apt.modalidade == "ONLINE"
                            else ""
                        )
                        + "Se precisar remarcar, fale com a Amanda pelo chat.\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )
                email_enviado = True
                enviados += 1
            except Exception:
                logger.exception("Falha ao enviar lembrete do atendimento %s", apt.pk)
                continue  # sem marcar: tenta de novo na próxima execução
        SessionReminder.objects.create(appointment=apt, email_enviado=email_enviado)

    return enviados
