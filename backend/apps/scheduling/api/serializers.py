from rest_framework import serializers

from apps.scheduling.models import Appointment, Availability


class AppointmentSerializer(serializers.ModelSerializer):
    patient_nome = serializers.CharField(source="patient.user.nome", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "patient",
            "patient_nome",
            "data_hora",
            "duracao_min",
            "modalidade",
            "status",
            "valor",
            "observacao",
            "created_at",
        )


class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ("id", "dia_semana", "hora_inicio", "hora_fim", "modalidade", "ativo")
