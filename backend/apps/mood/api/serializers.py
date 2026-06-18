from rest_framework import serializers

from apps.mood.models import MoodEntry


class MoodEntrySerializer(serializers.ModelSerializer):
    nivel_display = serializers.CharField(source="get_nivel_display", read_only=True)

    class Meta:
        model = MoodEntry
        fields = (
            "id",
            "data",
            "nivel",
            "nivel_display",
            "emocoes",
            "anotacao",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
        extra_kwargs = {"data": {"required": False}}
