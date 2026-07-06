"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { apiDownload } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatLongDate, formatTime } from "@/lib/format";
import { getPatientDashboard } from "@/lib/resources";
import type { PatientDashboard } from "@/lib/types";

export default function PacienteDashboard() {
  const { user } = useAuth();
  const [data, setData] = useState<PatientDashboard | null>(null);
  const [exportando, setExportando] = useState(false);

  useEffect(() => {
    getPatientDashboard().then(setData).catch(() => {});
  }, []);

  async function baixarMeusDados() {
    setExportando(true);
    try {
      const blob = await apiDownload("/me/export");
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `meus-dados-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("Não foi possível gerar a exportação agora. Tente novamente em instantes.");
    } finally {
      setExportando(false);
    }
  }

  const proximo = data?.proximo_atendimento;

  return (
    <DashboardShell role="PACIENTE">
      <h1 className="font-display text-3xl text-plum">Olá, {user?.nome?.split(" ")[0]}</h1>
      <p className="mt-1 text-ink/60">Bem-vindo(a) à sua área de atendimento.</p>

      <div className="mt-6 rounded-2xl border border-plum-200 bg-white p-6 shadow-card">
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

      <div className="mt-4 rounded-xl border border-plum-200 bg-white p-5 shadow-soft">
        <p className="text-sm text-ink/60">Sessões realizadas</p>
        <p className="mt-1 font-display text-3xl text-plum">{data?.sessoes_realizadas ?? "—"}</p>
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-plum-200 bg-white p-5 shadow-soft">
        <div>
          <p className="text-sm font-medium text-ink">Seus dados, seus direitos</p>
          <p className="text-xs text-ink/60">
            Baixe uma cópia de tudo que a plataforma guarda sobre você (LGPD).{" "}
            <Link href="/privacidade" className="text-plum underline">
              Política de privacidade
            </Link>
          </p>
        </div>
        <button
          onClick={baixarMeusDados}
          disabled={exportando}
          className="rounded-full border border-plum-400 px-5 py-2 font-brand text-xs uppercase tracking-widest text-plum transition-all duration-200 hover:bg-plum-200 active:scale-[0.98] disabled:opacity-60"
        >
          {exportando ? "Gerando…" : "Baixar meus dados"}
        </button>
      </div>
    </DashboardShell>
  );
}
