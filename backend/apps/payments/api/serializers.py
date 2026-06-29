from rest_framework import serializers

from apps.payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    patient_nome = serializers.CharField(source="patient.user.nome", read_only=True)
    appointment_data_hora = serializers.DateTimeField(
        source="appointment.data_hora", read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "patient",
            "patient_nome",
            "appointment",
            "appointment_data_hora",
            "valor",
            "status",
            "metodo",
            "provider_payment_id",
            "qr_code",
            "qr_code_base64",
            "link_pagamento",
            "pago_em",
            "created_at",
        ]
        read_only_fields = fields
