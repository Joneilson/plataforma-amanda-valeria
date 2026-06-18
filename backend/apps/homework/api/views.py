from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsPaciente, IsPsicologa
from apps.homework.selectors import homeworks_for
from apps.homework.services import HomeworkService

from .serializers import HomeworkSerializer


class HomeworkViewSet(viewsets.ModelViewSet):
    """Tarefas terapêuticas. Psicóloga cria/edita; paciente conclui as próprias."""

    serializer_class = HomeworkSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsPsicologa()]
        if self.action == "concluir":
            return [IsPaciente()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return homeworks_for(
            self.request.user, patient_id=self.request.query_params.get("patient")
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        homework = HomeworkService.create(criado_por=request.user, **serializer.validated_data)
        return Response(self.get_serializer(homework).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        homework = self.get_object()
        serializer = self.get_serializer(homework, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        homework = HomeworkService.update(homework, **serializer.validated_data)
        return Response(self.get_serializer(homework).data)

    @action(detail=True, methods=["post"])
    def concluir(self, request, pk=None):
        """Paciente marca a própria tarefa como concluída (ou reabre)."""
        homework = self.get_object()
        concluida = bool(request.data.get("concluida", True))
        homework = HomeworkService.set_concluida(homework, concluida)
        return Response(self.get_serializer(homework).data)
