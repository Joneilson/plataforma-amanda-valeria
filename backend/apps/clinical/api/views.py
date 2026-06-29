from rest_framework import generics, status, viewsets
from rest_framework.response import Response

from apps.accounts.permissions import IsPaciente, IsPsicologa
from apps.clinical.selectors import notes_for, records_for, shared_notes
from apps.clinical.services import ClinicalRecordService, PatientNoteService
from apps.patients.services import PatientService

from .serializers import ClinicalRecordSerializer, PatientNoteSerializer, SharedNoteSerializer


class ClinicalRecordViewSet(viewsets.ModelViewSet):
    """CRUD de evoluções clínicas — acesso exclusivo da psicóloga."""

    serializer_class = ClinicalRecordSerializer
    permission_classes = [IsPsicologa]

    def get_queryset(self):
        from apps.clinical.models import ClinicalRecord
        from apps.patients.models import Patient

        patient_id = self.request.query_params.get("patient")
        if patient_id:
            try:
                patient = Patient.objects.get(pk=patient_id)
            except Patient.DoesNotExist:
                return ClinicalRecord.objects.none()
            return records_for(patient)
        return ClinicalRecord.objects.select_related("patient__user", "appointment").all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        patient = data.pop("patient")
        record = ClinicalRecordService.create(patient, **data)
        return Response(self.get_serializer(record).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        record = self.get_object()
        serializer = self.get_serializer(record, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data.pop("patient", None)
        record = ClinicalRecordService.update(record, **data)
        return Response(self.get_serializer(record).data)


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
