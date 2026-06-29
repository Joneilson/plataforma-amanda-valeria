"""Camada de serviços de `video` — lógica de ESCRITA (regras de negócio)."""
import json
import urllib.error
import urllib.request
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.scheduling.models import Appointment

from .models import VideoRoom


class VideoService:
    DAILY_API = "https://api.daily.co/v1"

    @classmethod
    def _headers(cls):
        return {
            "Authorization": f"Bearer {settings.DAILY_API_KEY}",
            "Content-Type": "application/json",
        }

    @classmethod
    def _post(cls, path: str, payload: dict) -> dict:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{cls.DAILY_API}{path}",
            data=data,
            headers=cls._headers(),
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())

    @classmethod
    def get_or_create_room(cls, appointment: Appointment) -> VideoRoom:
        try:
            return appointment.video_room
        except VideoRoom.DoesNotExist:
            pass

        expira_em = appointment.data_hora + timedelta(hours=3)
        exp_ts = int(expira_em.timestamp())
        room_name = f"amanda-{appointment.pk}"

        room_resp = cls._post("/rooms", {
            "name": room_name,
            "privacy": "private",
            "properties": {
                "exp": exp_ts,
                "enable_chat": False,
                "enable_screenshare": False,
                "start_video_off": False,
                "start_audio_off": False,
            },
        })
        room_url: str = room_resp["url"]

        tok_psi = cls._post("/meeting-tokens", {
            "properties": {"room_name": room_name, "exp": exp_ts, "is_owner": True}
        })["token"]

        tok_pac = cls._post("/meeting-tokens", {
            "properties": {"room_name": room_name, "exp": exp_ts, "is_owner": False}
        })["token"]

        return VideoRoom.objects.create(
            appointment=appointment,
            room_name=room_name,
            room_url=room_url,
            token_paciente=tok_pac,
            token_psicologa=tok_psi,
            expira_em=expira_em,
        )
