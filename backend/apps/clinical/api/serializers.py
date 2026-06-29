from rest_framework import serializers

from apps.clinical.models import ClinicalRecord, PatientNote


class ClinicalRecordSerializer(serializers.ModelSerializer):
    """Evolução clínica — perspectiva da psicóloga."""

    appointment_data = serializers.SerializerMethodField()

    class Meta:
        model = ClinicalRecord
        fields = (
            "id",
            "patient",
            "appointment",
            "appointment_data",
            "conteudo",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "appointment_data", "created_at", "updated_at")

    def get_appointment_data(self, obj):
        if obj.appointment:
            return {
                "id": obj.appointment.id,
                "data_hora": obj.appointment.data_hora,
                "status": obj.appointment.status,
            }
        return None


class PatientNoteSerializer(serializers.ModelSerializer):
    """Anotação na perspectiva do paciente (dono)."""

    class Meta:
        model = PatientNote
        fields = (
            "id",
            "titulo",
            "conteudo",
            "compartilhar_com_psicologa",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class SharedNoteSerializer(serializers.ModelSerializer):
    """Anotação compartilhada, na perspectiva da psicóloga (somente leitura)."""

    patient_nome = serializers.CharField(source="patient.user.nome", read_only=True)
    patient = serializers.IntegerField(source="patient.id", read_only=True)

    class Meta:
        model = PatientNote
        fields = (
            "id",
            "patient",
            "patient_nome",
            "titulo",
            "conteudo",
            "created_at",
            "updated_at",
        )
