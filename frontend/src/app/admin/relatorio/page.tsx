"use client";

import { useCallback, useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { api } from "@/lib/api";
import { cardClass, compactButtonClass, inputClass, labelClass } from "@/lib/ui";

interface MonthlyReport {
  ano: number;
  mes: number;
  atendimentos: { total: number; por_status: Record<string, number> };
  financeiro: {
    recebido_no_mes: string;
    a_receber: string;
    pagamentos_pendentes: number;
  };
  por_paciente: { paciente: string; sessoes: number; valor_pago: string }[];
}

const MESES = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

const STATUS_LABEL: Record<string, string> = {
  AGENDADA: "Agendadas",
  CONFIRMADA: "Confirmadas",
  REALIZADA: "Realizadas",
  FALTA: "Faltas",
  CANCELADA: "Canceladas",
};

function brl(valor: string): string {
  return Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export default function RelatorioMensalPage() {
  const hoje = new Date();
  const [ano, setAno] = useState(hoje.getFullYear());
  const [mes, setMes] = useState(hoje.getMonth() + 1);
  const [report, setReport] = useState<MonthlyReport | null>(null);
  const [erro, setErro] = useState("");

  const carregar = useCallback(async () => {
    setErro("");
    try {
      setReport(await api<MonthlyReport>(`/reports/monthly?ano=${ano}&mes=${mes}`, {}, true));
    } catch {
      setErro("Não foi possível carregar o relatório.");
    }
  }, [ano, mes]);

  useEffect(() => {
    carregar();
  }, [carregar]);

  return (
    <DashboardShell role="PSICOLOGA">
      <div className="flex flex-wrap items-end justify-between gap-4 print:hidden">
        <div>
          <h1 className="font-display text-3xl text-plum">Relatório mensal</h1>
          <p className="mt-1 text-ink/60">Atendimentos e financeiro do mês.</p>
        </div>
        <div className="flex items-end gap-3">
          <div>
            <label className={labelClass}>Mês</label>
            <select
              value={mes}
              onChange={(e) => setMes(Number(e.target.value))}
              className={inputClass}
            >
              {MESES.map((nome, i) => (
                <option key={nome} value={i + 1}>{nome}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>Ano</label>
            <input
              type="number"
              value={ano}
              onChange={(e) => setAno(Number(e.target.value))}
              className={`${inputClass} w-28`}
            />
          </div>
          <button onClick={() => window.print()} className={compactButtonClass}>
            Imprimir / PDF
          </button>
        </div>
      </div>

      {erro && <p className="mt-4 text-danger">{erro}</p>}

      {report && (
        <div className="mt-6">
          <h2 className="hidden font-display text-2xl text-plum print:block">
            Relatório — {MESES[report.mes - 1]} de {report.ano}
          </h2>

          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            <div className={`${cardClass} p-5`}>
              <p className="text-sm text-ink/60">Atendimentos no mês</p>
              <p className="mt-1 font-display text-3xl text-plum">
                {report.atendimentos.total}
              </p>
            </div>
            <div className={`${cardClass} p-5`}>
              <p className="text-sm text-ink/60">Recebido no mês</p>
              <p className="mt-1 font-display text-3xl text-plum">
                {brl(report.financeiro.recebido_no_mes)}
              </p>
            </div>
            <div className={`${cardClass} p-5`}>
              <p className="text-sm text-ink/60">
                A receber ({report.financeiro.pagamentos_pendentes} pendentes)
              </p>
              <p className="mt-1 font-display text-3xl text-plum">
                {brl(report.financeiro.a_receber)}
              </p>
            </div>
          </div>

          <div className={`${cardClass} mt-4 p-5`}>
            <p className="font-brand text-xs uppercase tracking-[0.2em] text-plum-600">
              Sessões por status
            </p>
            <div className="mt-3 flex flex-wrap gap-4">
              {Object.entries(report.atendimentos.por_status).map(([status, total]) => (
                <div key={status} className="rounded-lg bg-sand px-4 py-2 text-sm">
                  <span className="text-ink/60">{STATUS_LABEL[status] ?? status}: </span>
                  <span className="font-medium text-ink">{total}</span>
                </div>
              ))}
              {Object.keys(report.atendimentos.por_status).length === 0 && (
                <p className="text-sm text-ink/60">Sem atendimentos neste mês.</p>
              )}
            </div>
          </div>

          <div className={`${cardClass} mt-4 overflow-x-auto p-5`}>
            <p className="font-brand text-xs uppercase tracking-[0.2em] text-plum-600">
              Recebimentos por paciente
            </p>
            {report.por_paciente.length ? (
              <table className="mt-3 w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-plum-200 text-ink/60">
                    <th className="py-2 font-normal">Paciente</th>
                    <th className="py-2 font-normal">Pagamentos</th>
                    <th className="py-2 font-normal">Valor pago</th>
                  </tr>
                </thead>
                <tbody>
                  {report.por_paciente.map((row) => (
                    <tr key={row.paciente} className="border-b border-plum-200/50">
                      <td className="py-2">{row.paciente}</td>
                      <td className="py-2">{row.sessoes}</td>
                      <td className="py-2">{brl(row.valor_pago)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="mt-3 text-sm text-ink/60">Nenhum recebimento neste mês.</p>
            )}
          </div>
        </div>
      )}
    </DashboardShell>
  );
}
