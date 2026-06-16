from rest_framework import serializers

from apps.accounts.api.serializers import UserSerializer
from apps.patients.models import Patient

CLINICAL_FIELDS = (
    "data_nascimento",
    "genero",
    "queixa_principal",
    "contato_emergencia_nome",
    "contato_emergencia_telefone",
    "status",
    "inicio_tratamento",
    "valor_sessao",
)


class PatientSerializer(serializers.ModelSerializer):
    """Saída completa do paciente (com a conta aninhada)."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = ("id", "user", *CLINICAL_FIELDS, "created_at")


class PatientCreateSerializer(serializers.Serializer):
    # Dados da conta
    email = serializers.EmailField()
    nome = serializers.CharField(max_length=150)
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    # Dados clínicos
    data_nascimento = serializers.DateField(required=False, allow_null=True)
    genero = serializers.CharField(max_length=40, required=False, allow_blank=True, default="")
    queixa_principal = serializers.CharField(required=False, allow_blank=True, default="")
    contato_emergencia_nome = serializers.CharField(
        max_length=150, required=False, allow_blank=True, default=""
    )
    contato_emergencia_telefone = serializers.CharField(
        max_length=20, required=False, allow_blank=True, default=""
    )
    status = serializers.ChoiceField(
        choices=Patient.Status.choices, required=False, default=Patient.Status.ATIVO
    )
    inicio_tratamento = serializers.DateField(required=False)
    valor_sessao = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True
    )


class PatientUpdateSerializer(serializers.ModelSerializer):
    """Edição dos dados clínicos (a conta é gerida à parte)."""

    class Meta:
        model = Patient
        fields = CLINICAL_FIELDS
