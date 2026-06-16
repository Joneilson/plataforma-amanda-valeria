"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { getAdminMetrics } from "@/lib/resources";
import type { AdminMetrics } from "@/lib/types";

function Card({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-plum-200 bg-white p-5">
      <p className="text-sm text-ink/60">{label}</p>
      <p className="mt-1 font-display text-3xl text-plum">{value}</p>
    </div>
  );
}

function ModalidadeBar({ online, presencial }: { online: number; presencial: number }) {
  const total = online + presencial;
  const pct = (n: number) => (total === 0 ? 0 : Math.round((n / total) * 100));
  return (
    <div className="rounded-xl border border-plum-200 bg-white p-5">
      <p className="mb-3 text-sm text-ink/60">Atendimentos: online vs. presencial</p>
      {total === 0 ? (
        <p className="text-sm text-ink/50">Ainda sem atendimentos realizados.</p>
      ) : (
        <div className="space-y-3">
          {[
            { label: "Online", n: online, color: "bg-plum-600" },
            { label: "Presencial", n: presencial, color: "bg-plum-400" },
          ].map((row) => (
            <div key={row.label}>
              <div className="mb-1 flex justify-between text-sm text-ink/70">
                <span>{row.label}</span>
                <span>
                  {row.n} ({pct(row.n)}%)
                </span>
              </div>
              <div className="h-2.5 w-full overflow-hidden rounded-full bg-sand">
                <div className={`h-full ${row.color}`} style={{ width: `${pct(row.n)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    getAdminMetrics().then(setMetrics).catch(() => setError(true));
  }, []);

  return (
    <DashboardShell role="PSICOLOGA">
      <h1 className="font-display text-3xl text-plum">Dashboard</h1>
      <p className="mt-1 text-ink/60">Visão geral da sua prática.</p>

      {error && <p className="mt-6 text-sm text-danger">Não foi possível carregar as métricas.</p>}

      {metrics && (
        <>
          <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
            <Card label="Atendimentos realizados" value={metrics.atendimentos_realizados} />
            <Card label="Horas atendidas" value={`${metrics.horas_atendidas}h`} />
            <Card label="Pacientes ativos" value={metrics.pacientes_ativos} />
            <Card label="Próximos 7 dias" value={metrics.proximos_7_dias} />
          </div>
          <div className="mt-4 grid gap-4 lg:grid-cols-2">
            <ModalidadeBar online={metrics.online} presencial={metrics.presencial} />
            <Card label="Faltas" value={metrics.faltas} />
          </div>
        </>
      )}
    </DashboardShell>
  );
}
