from rest_framework import status, viewsets
from rest_framework.response import Response

from apps.accounts.permissions import IsPsicologa
from apps.patients.selectors import list_patients
from apps.patients.services import PatientService

from .serializers import PatientCreateSerializer, PatientSerializer, PatientUpdateSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """CRUD de pacientes — exclusivo da psicóloga."""

    permission_classes = [IsPsicologa]

    def get_queryset(self):
        return list_patients(
            status=self.request.query_params.get("status"),
            search=self.request.query_params.get("search"),
        )

    def get_serializer_class(self):
        if self.action == "create":
            return PatientCreateSerializer
        if self.action in ("update", "partial_update"):
            return PatientUpdateSerializer
        return PatientSerializer

    def create(self, request, *args, **kwargs):
        serializer = PatientCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        patient = PatientService.create_with_account(
            email=data.pop("email"),
            nome=data.pop("nome"),
            telefone=data.pop("telefone", ""),
            **data,
        )
        return Response(PatientSerializer(patient).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        patient = self.get_object()
        serializer = PatientUpdateSerializer(patient, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        PatientService.update(patient, **serializer.validated_data)
        return Response(PatientSerializer(patient).data)
