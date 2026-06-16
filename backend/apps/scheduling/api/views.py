from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsPaciente, IsPsicologa
from apps.patients.services import PatientService
from apps.scheduling.models import Appointment
from apps.scheduling.selectors import (
    admin_metrics,
    appointments_for,
    next_appointment_for_patient,
)

from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    """Atendimentos. Leitura conforme o papel; escrita só da psicóloga."""

    serializer_class = AppointmentSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsPsicologa()]

    def get_queryset(self):
        return appointments_for(self.request.user)


class AdminDashboardView(APIView):
    permission_classes = [IsPsicologa]

    def get(self, request):
        return Response(admin_metrics())


class PatientDashboardView(APIView):
    permission_classes = [IsPaciente]

    def get(self, request):
        patient = PatientService.ensure_profile(request.user)
        proximo = next_appointment_for_patient(patient)
        return Response(
            {
                "proximo_atendimento": (
                    AppointmentSerializer(proximo).data if proximo else None
                ),
                "sessoes_realizadas": patient.appointments.filter(
                    status=Appointment.Status.REALIZADA
                ).count(),
            }
        )
