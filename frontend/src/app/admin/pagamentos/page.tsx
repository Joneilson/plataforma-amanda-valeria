"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { formatDateTime } from "@/lib/format";
import { listAllPayments, markPaymentAsPaid } from "@/lib/resources";
import type { Payment } from "@/lib/types";
import { cardClass, compactButtonClass } from "@/lib/ui";

const STATUS_LABEL: Record<string, string> = {
  PENDENTE: "Pendente",
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

export default function AdminPagamentosPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [marking, setMarking] = useState<number | null>(null);

  function refresh() {
    listAllPayments()
      .then(setPayments)
      .catch(() => {})
      .finally(() => setLoading(false));
  }

  useEffect(() => { refresh(); }, []);

  const totalPago = payments.filter((p) => p.status === "PAGO").reduce((s, p) => s + Number(p.valor), 0);
  const totalPendente = payments.filter((p) => p.status === "PENDENTE").reduce((s, p) => s + Number(p.valor), 0);

  async function handleMarcarPago(paymentId: number) {
    setMarking(paymentId);
    try {
      const updated = await markPaymentAsPaid(paymentId);
      setPayments((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
    } finally {
      setMarking(null);
    }
  }

  return (
    <DashboardShell role="PSICOLOGA">
      <h1 className="font-display text-3xl text-plum">Pagamentos</h1>
      <p className="mt-1 text-sm text-ink/60">Controle financeiro e cobranças via PIX.</p>

      <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-3">
        <div className="rounded-xl border border-plum-200 bg-white p-5 shadow-soft">
          <p className="text-sm text-ink/60">Total recebido</p>
          <p className="mt-1 font-display text-2xl text-green-700">
            R$ {totalPago.toFixed(2).replace(".", ",")}
          </p>
        </div>
        <div className="rounded-xl border border-plum-200 bg-white p-5 shadow-soft">
          <p className="text-sm text-ink/60">A receber</p>
          <p className="mt-1 font-display text-2xl text-amber-600">
            R$ {totalPendente.toFixed(2).replace(".", ",")}
          </p>
        </div>
        <div className="rounded-xl border border-plum-200 bg-white p-5 shadow-soft col-span-2 lg:col-span-1">
          <p className="text-sm text-ink/60">Total de cobranças</p>
          <p className="mt-1 font-display text-2xl text-plum">{payments.length}</p>
        </div>
      </div>

      <div className={`mt-6 overflow-x-auto ${cardClass}`}>
        {loading ? (
          <p className="px-5 py-8 text-center text-sm text-ink/50">Carregando…</p>
        ) : payments.length === 0 ? (
          <p className="px-5 py-8 text-center text-sm text-ink/50">Nenhuma cobrança registrada.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-plum-200 text-left text-ink/50">
                <th className="px-4 py-3 font-medium">Paciente</th>
                <th className="px-4 py-3 font-medium">Sessão</th>
                <th className="px-4 py-3 font-medium">Valor</th>
                <th className="px-4 py-3 font-medium">Método</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Pago em</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {payments.map((p) => (
                <tr key={p.id} className="border-b border-plum-100/50 last:border-0 hover:bg-sand-light">
                  <td className="px-4 py-3 font-medium text-ink">{p.patient_nome}</td>
                  <td className="px-4 py-3 text-ink/70">
                    {p.appointment_data_hora ? formatDateTime(p.appointment_data_hora) : "—"}
                  </td>
                  <td className="px-4 py-3 text-ink">
                    R$ {Number(p.valor).toFixed(2).replace(".", ",")}
                  </td>
                  <td className="px-4 py-3 text-ink/70">{METODO_LABEL[p.metodo]}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_COLOR[p.status]}`}>
                      {STATUS_LABEL[p.status]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-ink/60">
                    {p.pago_em ? formatDateTime(p.pago_em) : "—"}
                  </td>
                  <td className="px-4 py-3">
                    {p.status === "PENDENTE" && (
                      <button
                        onClick={() => handleMarcarPago(p.id)}
                        disabled={marking === p.id}
                        className={compactButtonClass}
                      >
                        {marking === p.id ? "…" : "Marcar pago"}
                      </button>
                    )}
                    {p.status === "PENDENTE" && p.link_pagamento && (
                      <a
                        href={p.link_pagamento}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-2 text-xs text-plum underline"
                      >
                        Ver link
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
