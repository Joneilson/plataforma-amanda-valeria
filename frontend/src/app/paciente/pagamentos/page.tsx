"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { ApiError } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { createPayment, listAppointments, listMyPayments } from "@/lib/resources";
import type { Appointment, Payment, PaymentMetodo } from "@/lib/types";
import { cardClass, compactButtonClass } from "@/lib/ui";

const STATUS_LABEL: Record<string, string> = {
  PENDENTE: "Aguardando pagamento",
  PAGO: "Pago",
  FALHOU: "Falhou",
  ESTORNADO: "Estornado",
};

const STATUS_COLOR: Record<string, string> = {
  PENDENTE: "text-amber-600 bg-amber-50",
  PAGO: "text-green-700 bg-green-50",
  FALHOU: "text-red-600 bg-red-50",
  ESTORNADO: "text-ink/50 bg-sand",
};

const METODO_LABEL: Record<string, string> = {
  PIX: "Pix",
  CARTAO: "Cartão",
  MANUAL: "Manual",
};

function PixQrModal({ payment, onClose }: { payment: Payment; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 backdrop-blur-sm">
      <div className={`${cardClass} w-full max-w-sm p-6 text-center`}>
        <h2 className="font-display text-2xl text-plum">Pague via PIX</h2>
        <p className="mt-1 text-sm text-ink/60">
          Valor: <strong>R$ {Number(payment.valor).toFixed(2).replace(".", ",")}</strong>
        </p>

        {payment.qr_code_base64 && (
          <img
            src={`data:image/png;base64,${payment.qr_code_base64}`}
            alt="QR Code PIX"
            className="mx-auto mt-4 h-48 w-48 rounded-xl border border-plum-200"
          />
        )}

        {payment.qr_code && (
          <div className="mt-4">
            <p className="mb-1 text-xs text-ink/50">Ou copie o código:</p>
            <textarea
              readOnly
              value={payment.qr_code}
              className="w-full resize-none rounded-lg border border-plum-200 bg-sand p-2 text-xs text-ink/70"
              rows={4}
              onClick={(e) => (e.target as HTMLTextAreaElement).select()}
            />
            <button
              onClick={() => navigator.clipboard.writeText(payment.qr_code)}
              className="mt-2 text-xs text-plum underline"
            >
              Copiar código PIX
            </button>
          </div>
        )}

        <p className="mt-4 text-xs text-ink/50">
          Após o pagamento, o status será atualizado pela psicóloga.
        </p>

        <button onClick={onClose} className={`mt-5 w-full ${compactButtonClass}`}>
          Fechar
        </button>
      </div>
    </div>
  );
}

type GeneratingKey = `${number}-${"PIX" | "CARTAO"}`;

export default function PacientePagamentosPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [selectedQr, setSelectedQr] = useState<Payment | null>(null);
  const [generating, setGenerating] = useState<GeneratingKey | null>(null);
  const [error, setError] = useState("");

  function refresh() {
    listMyPayments().then(setPayments).catch(() => {});
  }

  useEffect(() => {
    refresh();
    listAppointments().then(setAppointments).catch(() => {});
  }, []);

  const paidIds = new Set(payments.filter((p) => p.appointment).map((p) => p.appointment));
  const pendingAppointments = appointments.filter(
    (a) =>
      (a.status === "REALIZADA" || a.status === "CONFIRMADA") && !paidIds.has(a.id),
  );

  async function handleGerar(appointmentId: number, metodo: PaymentMetodo) {
    setError("");
    const key: GeneratingKey = `${appointmentId}-${metodo as "PIX" | "CARTAO"}`;
    setGenerating(key);
    try {
      const payment = await createPayment(appointmentId, metodo as "PIX" | "CARTAO");
      setPayments((prev) => [payment, ...prev]);
      if (metodo === "PIX") {
        setSelectedQr(payment);
      } else if (payment.link_pagamento) {
        window.open(payment.link_pagamento, "_blank", "noopener,noreferrer");
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Não foi possível gerar a cobrança.");
    } finally {
      setGenerating(null);
    }
  }

  return (
    <DashboardShell role="PACIENTE">
      {selectedQr && <PixQrModal payment={selectedQr} onClose={() => setSelectedQr(null)} />}

      <h1 className="font-display text-3xl text-plum">Pagamentos</h1>
      <p className="mt-1 text-sm text-ink/60">Gerencie suas cobranças e pague via PIX ou cartão.</p>

      {error && (
        <p className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
          {error}
        </p>
      )}

      {pendingAppointments.length > 0 && (
        <div className={`mt-6 ${cardClass} p-5`}>
          <h2 className="mb-3 font-brand text-xs uppercase tracking-widest text-plum-600">
            Sessões sem pagamento
          </h2>
          <ul className="space-y-2">
            {pendingAppointments.map((a) => (
              <li
                key={a.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-plum-100 bg-sand-light p-3"
              >
                <div>
                  <p className="text-sm font-medium text-ink">{formatDateTime(a.data_hora)}</p>
                  <p className="text-xs text-ink/50">{a.modalidade === "ONLINE" ? "Online" : "Presencial"}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleGerar(a.id, "PIX")}
                    disabled={generating !== null}
                    className={compactButtonClass}
                  >
                    {generating === `${a.id}-PIX` ? "Gerando…" : "Pagar via PIX"}
                  </button>
                  <button
                    onClick={() => handleGerar(a.id, "CARTAO")}
                    disabled={generating !== null}
                    className="rounded-full border border-plum px-3 py-1.5 text-xs font-medium text-plum transition-colors hover:bg-plum-100 disabled:opacity-50"
                  >
                    {generating === `${a.id}-CARTAO` ? "Abrindo…" : "Pagar com Cartão"}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className={`mt-6 overflow-x-auto ${cardClass}`}>
        <h2 className="border-b border-plum-100 px-5 py-3 font-brand text-xs uppercase tracking-widest text-plum-600">
          Histórico
        </h2>
        {payments.length === 0 ? (
          <p className="px-5 py-8 text-center text-sm text-ink/50">Nenhum pagamento ainda.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-plum-100 text-left text-ink/50">
                <th className="px-5 py-3 font-medium">Sessão</th>
                <th className="px-5 py-3 font-medium">Valor</th>
                <th className="px-5 py-3 font-medium">Método</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {payments.map((p) => (
                <tr key={p.id} className="border-b border-plum-100/50 last:border-0 hover:bg-sand-light">
                  <td className="px-5 py-3 text-ink/70">
                    {p.appointment_data_hora ? formatDateTime(p.appointment_data_hora) : "—"}
                  </td>
                  <td className="px-5 py-3 font-medium text-ink">
                    R$ {Number(p.valor).toFixed(2).replace(".", ",")}
                  </td>
                  <td className="px-5 py-3 text-ink/60">{METODO_LABEL[p.metodo]}</td>
                  <td className="px-5 py-3">
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLOR[p.status]}`}>
                      {STATUS_LABEL[p.status]}
                    </span>
                  </td>
                  <td className="px-5 py-3">
                    {p.status === "PENDENTE" && p.qr_code && (
                      <button
                        onClick={() => setSelectedQr(p)}
                        className="text-xs text-plum underline"
                      >
                        Ver QR Code
                      </button>
                    )}
                    {p.status === "PENDENTE" && p.link_pagamento && (
                      <a
                        href={p.link_pagamento}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-plum underline"
                      >
                        Pagar com Cartão
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </DashboardShell>
  );
}
