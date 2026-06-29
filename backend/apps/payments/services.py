"""Camada de serviços de `payments` — geração de PIX (BRCode/EMV) local."""
import base64
import logging
from decimal import Decimal
from io import BytesIO

from django.conf import settings
from django.utils import timezone

from .models import Payment

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Geração do payload PIX (padrão BACEN / EMV Merchant Presented QR Code)
# ---------------------------------------------------------------------------

def _f(id_: str, value: str) -> str:
    return f"{id_}{len(value):02d}{value}"


def _crc16(payload: str) -> str:
    crc = 0xFFFF
    for char in payload:
        crc ^= ord(char) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return format(crc, "04X")


def _build_pix_payload(key: str, nome: str, cidade: str, valor: Decimal, txid: str) -> str:
    nome = nome[:25]
    cidade = cidade[:15]
    txid = "".join(c for c in txid if c.isalnum())[:25] or "Amanda"

    merchant_info = _f("26", _f("00", "BR.GOV.BCB.PIX") + _f("01", key))
    additional = _f("62", _f("05", txid))

    body = (
        _f("00", "01")
        + merchant_info
        + _f("52", "0000")
        + _f("53", "986")
        + _f("54", f"{valor:.2f}")
        + _f("58", "BR")
        + _f("59", nome)
        + _f("60", cidade)
        + additional
        + "6304"
    )
    return body + _crc16(body)


def _pix_qr_base64(payload: str) -> str:
    import qrcode

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# ---------------------------------------------------------------------------
# Serviço público
# ---------------------------------------------------------------------------

class PixService:
    @classmethod
    def create_pix(cls, appointment, patient) -> Payment:
        """Gera QR Code PIX localmente e persiste o Payment. Idempotente."""
        try:
            return appointment.payment
        except Payment.DoesNotExist:
            pass

        pix_key = getattr(settings, "PIX_KEY", "")
        if not pix_key:
            raise ValueError("PIX_KEY não configurada nas variáveis de ambiente.")

        nome = getattr(settings, "PIX_TITULAR", "Amanda Valeria")
        cidade = getattr(settings, "PIX_CIDADE", "Recife")
        valor = appointment.valor or patient.valor_sessao or Decimal("0.01")
        txid = f"AMN{appointment.pk:010d}"

        payload = _build_pix_payload(pix_key, nome, cidade, valor, txid)
        qr_b64 = _pix_qr_base64(payload)

        return Payment.objects.create(
            appointment=appointment,
            patient=patient,
            valor=valor,
            metodo=Payment.Metodo.PIX,
            provider="infinitypay",
            qr_code=payload,
            qr_code_base64=qr_b64,
            status=Payment.Status.PENDENTE,
        )

    @classmethod
    def create_cartao(cls, appointment, patient) -> Payment:
        """Cria registro de pagamento via cartão com link InfinityPay. Idempotente."""
        try:
            return appointment.payment
        except Payment.DoesNotExist:
            pass

        link = getattr(settings, "INFINITYPAY_LINK_CREDITO", "")
        if not link:
            raise ValueError("INFINITYPAY_LINK_CREDITO não configurada nas variáveis de ambiente.")

        valor = appointment.valor or patient.valor_sessao or Decimal("0.01")

        return Payment.objects.create(
            appointment=appointment,
            patient=patient,
            valor=valor,
            metodo=Payment.Metodo.CARTAO,
            provider="infinitypay",
            link_pagamento=link,
            status=Payment.Status.PENDENTE,
        )

    @classmethod
    def mark_as_paid(cls, payment: Payment) -> Payment:
        payment.status = Payment.Status.PAGO
        payment.metodo = Payment.Metodo.MANUAL
        payment.pago_em = timezone.now()
        payment.save(update_fields=["status", "metodo", "pago_em", "updated_at"])
        return payment
