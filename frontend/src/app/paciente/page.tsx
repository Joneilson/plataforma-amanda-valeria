"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { useAuth } from "@/lib/auth";
import { formatLongDate, formatTime } from "@/lib/format";
import { getPatientDashboard } from "@/lib/resources";
import type { PatientDashboard } from "@/lib/types";

export default function PacienteDashboard() {
  const { user } = useAuth();
  const [data, setData] = useState<PatientDashboard | null>(null);

  useEffect(() => {
    getPatientDashboard().then(setData).catch(() => {});
  }, []);

  const proximo = data?.proximo_atendimento;

  return (
    <DashboardShell role="PACIENTE">
      <h1 className="font-display text-3xl text-plum">Olá, {user?.nome?.split(" ")[0]}</h1>
      <p className="mt-1 text-ink/60">Bem-vindo(a) à sua área de atendimento.</p>

      <div className="mt-6 rounded-2xl border border-plum-200 bg-white p-6">
        <p className="font-brand text-xs uppercase tracking-[0.2em] text-plum-600">
          Próximo atendimento
        </p>
        {proximo ? (
          <div className="mt-3">
            <p className="font-display text-3xl capitalize text-plum">
              {formatLongDate(proximo.data_hora)}
            </p>
            <p className="mt-1 text-ink/70">
              às {formatTime(proximo.data_hora)} ·{" "}
              {proximo.modalidade === "ONLINE" ? "Online" : "Presencial"} ·{" "}
              {proximo.duracao_min} min
            </p>
          </div>
        ) : (
          <p className="mt-3 text-ink/60">Você não tem atendimentos agendados no momento.</p>
        )}
      </div>

      <div className="mt-4 rounded-xl border border-plum-200 bg-white p-5">
        <p className="text-sm text-ink/60">Sessões realizadas</p>
        <p className="mt-1 font-display text-3xl text-plum">{data?.sessoes_realizadas ?? "—"}</p>
      </div>
    </DashboardShell>
  );
}
