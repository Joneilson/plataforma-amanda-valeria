import logging

from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.permissions import IsPaciente, IsPsicologa
from apps.patients.models import Patient
from apps.payments.models import Payment
from apps.payments.selectors import all_payments, payments_for_patient
from apps.payments.services import PixService
from apps.scheduling.models import Appointment

from .serializers import PaymentSerializer

logger = logging.getLogger(__name__)


class CheckoutPixView(APIView):
    """POST /api/payments/checkout  — gera QR Code PIX para um atendimento."""

    permission_classes = [IsPaciente]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "checkout"

    def post(self, request):
        appointment_id = request.data.get("appointment_id")
        if not appointment_id:
            return Response({"detail": "appointment_id obrigatório."}, status=400)

        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            return Response({"detail": "Perfil de paciente não encontrado."}, status=403)

        try:
            apt = Appointment.objects.get(pk=appointment_id, patient=patient)
        except Appointment.DoesNotExist:
            return Response({"detail": "Atendimento não encontrado."}, status=404)

        metodo = request.data.get("metodo", "PIX").upper()

        try:
            if metodo == "CARTAO":
                payment = PixService.create_cartao(apt, patient)
            else:
                payment = PixService.create_pix(apt, patient)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=503)
        except Exception as exc:
            logger.error("Erro ao gerar cobrança: %s", exc)
            return Response({"detail": "Erro ao gerar cobrança."}, status=500)

        return Response(PaymentSerializer(payment).data, status=201)


class MyPaymentsView(APIView):
    """GET /api/payments/my  — lista pagamentos do paciente autenticado."""

    permission_classes = [IsPaciente]

    def get(self, request):
        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            return Response([], status=200)

        qs = payments_for_patient(patient)
        return Response(PaymentSerializer(qs, many=True).data)


class PaymentAdminListView(APIView):
    """GET /api/payments  — lista todos os pagamentos (psicóloga)."""

    permission_classes = [IsPsicologa]

    def get(self, request):
        qs = all_payments()
        return Response(PaymentSerializer(qs, many=True).data)


class MarkAsPaidView(APIView):
    """POST /api/payments/<id>/marcar-pago  — marca como pago manualmente."""

    permission_classes = [IsPsicologa]

    def post(self, request, payment_id):
        try:
            payment = Payment.objects.get(pk=payment_id)
        except Payment.DoesNotExist:
            return Response({"detail": "Pagamento não encontrado."}, status=404)

        payment = PixService.mark_as_paid(payment)
        return Response(PaymentSerializer(payment).data)
