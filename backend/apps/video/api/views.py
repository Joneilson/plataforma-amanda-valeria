import logging
import urllib.error

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.patients.models import Patient
from apps.scheduling.models import Appointment
from apps.video.services import VideoService

from .serializers import VideoRoomSerializer

logger = logging.getLogger(__name__)


class VideoRoomView(APIView):
    """
    POST /api/video/rooms/<appointment_id>
    Cria (ou recupera) a sala Daily.co para o atendimento.
    Retorna o token correto para o papel do usuário autenticado.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        try:
            apt = Appointment.objects.select_related("patient__user").get(pk=appointment_id)
        except Appointment.DoesNotExist:
            return Response({"detail": "Atendimento não encontrado."}, status=404)

        if request.user.is_paciente:
            try:
                patient = Patient.objects.get(user=request.user)
            except Patient.DoesNotExist:
                return Response({"detail": "Perfil de paciente não encontrado."}, status=403)
            if apt.patient_id != patient.pk:
                return Response({"detail": "Sem permissão para este atendimento."}, status=403)

        if apt.modalidade != "ONLINE":
            return Response({"detail": "Este atendimento não é online."}, status=400)

        if not hasattr(apt, "video_room"):
            from django.conf import settings

            if not getattr(settings, "DAILY_API_KEY", ""):
                return Response(
                    {"detail": "Integração de vídeo não configurada (DAILY_API_KEY ausente)."},
                    status=503,
                )

        try:
            room = VideoService.get_or_create_room(apt)
        except urllib.error.HTTPError as exc:
            logger.error("Daily.co retornou erro HTTP %s %s", exc.code, exc.reason)
            return Response({"detail": "Erro ao criar sala de vídeo."}, status=502)
        except Exception:
            logger.exception("Falha ao conectar ao Daily.co")
            return Response({"detail": "Erro ao conectar ao serviço de vídeo."}, status=502)

        return Response(VideoRoomSerializer(room, context={"request": request}).data)
