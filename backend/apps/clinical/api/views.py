from rest_framework import generics, status, viewsets
from rest_framework.response import Response

from apps.accounts.permissions import IsPaciente, IsPsicologa
from apps.clinical.selectors import notes_for, shared_notes
from apps.clinical.services import PatientNoteService
from apps.patients.services import PatientService

from .serializers import PatientNoteSerializer, SharedNoteSerializer


class PatientNoteViewSet(viewsets.ModelViewSet):
    """CRUD das anotações pessoais — cada paciente acessa só as próprias."""

    serializer_class = PatientNoteSerializer
    permission_classes = [IsPaciente]

    def get_patient(self):
        return PatientService.ensure_profile(self.request.user)

    def get_queryset(self):
        return notes_for(self.get_patient())

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note = PatientNoteService.create(self.get_patient(), **serializer.validated_data)
        return Response(self.get_serializer(note).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        note = self.get_object()
        serializer = self.get_serializer(note, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        note = PatientNoteService.update(note, **serializer.validated_data)
        return Response(self.get_serializer(note).data)


class SharedNoteListView(generics.ListAPIView):
    """Anotações compartilhadas pelos pacientes — leitura da psicóloga."""

    serializer_class = SharedNoteSerializer
    permission_classes = [IsPsicologa]

    def get_queryset(self):
        return shared_notes()
