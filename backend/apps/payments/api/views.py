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


class MonthlyReportView(APIView):
    """GET /api/reports/monthly?ano=2026&mes=7 — resumo do mês (psicóloga).

    Atendimentos por status + financeiro (recebido no mês, pendências) e
    detalhamento por paciente. O frontend renderiza em layout imprimível.
    """

    permission_classes = [IsPsicologa]

    def get(self, request):
        from django.db.models import Count, Sum
        from django.utils import timezone

        hoje = timezone.localdate()
        try:
            ano = int(request.query_params.get("ano", hoje.year))
            mes = int(request.query_params.get("mes", hoje.month))
            if not 1 <= mes <= 12:
                raise ValueError
        except (TypeError, ValueError):
            return Response({"detail": "Parâmetros ano/mes inválidos."}, status=400)

        atendimentos = Appointment.objects.filter(
            data_hora__year=ano, data_hora__month=mes
        )
        por_status = {
            row["status"]: row["total"]
            for row in atendimentos.values("status").annotate(total=Count("id"))
        }

        pagos = Payment.objects.filter(
            status=Payment.Status.PAGO, pago_em__year=ano, pago_em__month=mes
        )
        recebido = pagos.aggregate(total=Sum("valor"))["total"] or 0
        pendentes = Payment.objects.filter(
            status=Payment.Status.PENDENTE,
            appointment__data_hora__year=ano,
            appointment__data_hora__month=mes,
        )
        a_receber = pendentes.aggregate(total=Sum("valor"))["total"] or 0

        por_paciente = [
            {
                "paciente": row["patient__user__nome"],
                "sessoes": row["sessoes"],
                "valor_pago": f"{row['valor_pago'] or 0:.2f}",
            }
            for row in pagos.values("patient__user__nome").annotate(
                sessoes=Count("id"), valor_pago=Sum("valor")
            ).order_by("patient__user__nome")
        ]

        return Response(
            {
                "ano": ano,
                "mes": mes,
                "atendimentos": {
                    "total": atendimentos.count(),
                    "por_status": por_status,
                },
                "financeiro": {
                    "recebido_no_mes": f"{recebido:.2f}",
                    "a_receber": f"{a_receber:.2f}",
                    "pagamentos_pendentes": pendentes.count(),
                },
                "por_paciente": por_paciente,
            }
        )
