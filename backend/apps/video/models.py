from django.db import models

from apps.common.models import TimeStampedModel


class VideoRoom(TimeStampedModel):
    """Sala de videochamada gerada via Daily.co para um atendimento online."""

    appointment = models.OneToOneField(
        "scheduling.Appointment", on_delete=models.CASCADE, related_name="video_room"
    )
    provider = models.CharField(max_length=20, default="daily")
    room_name = models.CharField(max_length=120)
    room_url = models.URLField()
    token_paciente = models.TextField()
    token_psicologa = models.TextField()
    expira_em = models.DateTimeField()

    class Meta:
        verbose_name = "sala de vídeo"
        verbose_name_plural = "salas de vídeo"

    def __str__(self):
        return f"Sala {self.room_name} — {self.appointment}"
