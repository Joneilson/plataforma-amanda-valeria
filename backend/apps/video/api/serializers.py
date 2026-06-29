from rest_framework import serializers

from apps.video.models import VideoRoom


class VideoRoomSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = VideoRoom
        fields = ["id", "room_name", "room_url", "token", "expira_em"]

    def get_token(self, obj: VideoRoom) -> str:
        request = self.context.get("request")
        if request and request.user.is_psicologa:
            return obj.token_psicologa
        return obj.token_paciente
