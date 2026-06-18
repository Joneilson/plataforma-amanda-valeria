from rest_framework import serializers

from apps.clinical.models import PatientNote


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
