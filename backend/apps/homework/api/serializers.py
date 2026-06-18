from rest_framework import serializers

from apps.homework.models import Homework


class HomeworkSerializer(serializers.ModelSerializer):
    patient_nome = serializers.CharField(source="patient.user.nome", read_only=True)
    criado_por_nome = serializers.CharField(source="criado_por.nome", read_only=True)

    class Meta:
        model = Homework
        fields = (
            "id",
            "patient",
            "patient_nome",
            "criado_por_nome",
            "titulo",
            "descricao",
            "prazo",
            "status",
            "concluida_em",
            "created_at",
        )
        read_only_fields = (
            "id",
            "patient_nome",
            "criado_por_nome",
            "status",
            "concluida_em",
            "created_at",
        )
