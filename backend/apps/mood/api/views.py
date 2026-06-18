from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsPaciente
from apps.mood.selectors import mood_entries_for, mood_insights
from apps.mood.services import MoodService
from apps.patients.services import PatientService

from .serializers import MoodEntrySerializer


class MoodViewSet(viewsets.ModelViewSet):
    """Humor diário do paciente. Cada paciente acessa apenas o próprio histórico."""

    serializer_class = MoodEntrySerializer
    permission_classes = [IsPaciente]
    http_method_names = ["get", "post", "head", "options"]

    def get_patient(self):
        return PatientService.ensure_profile(self.request.user)

    def get_queryset(self):
        return mood_entries_for(self.get_patient())

    def create(self, request, *args, **kwargs):
        """Registra um novo humor. Atualizar = novo registro (preserva o anterior)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = MoodService.register(self.get_patient(), **serializer.validated_data)
        return Response(self.get_serializer(entry).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def insights(self, request):
        dias = int(request.query_params.get("dias", 30))
        return Response(mood_insights(self.get_patient(), dias=dias))
