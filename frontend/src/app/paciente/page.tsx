"use client";

import { DashboardShell } from "@/components/DashboardShell";
import { useAuth } from "@/lib/auth";

export default function PacienteDashboard() {
  const { user } = useAuth();
  return (
    <DashboardShell role="PACIENTE">
      <h1 className="font-display text-4xl text-plum">Olá, {user?.nome?.split(" ")[0]} 👋</h1>
      <p className="mt-3 text-ink/70">
        Bem-vindo(a) à sua área de atendimento. Em breve, aqui ficará seu próximo
        atendimento, o registro de humor diário, suas anotações e a sala de vídeo.
      </p>
      <p className="mt-6 font-brand text-xs uppercase tracking-widest text-plum-400">
        Painel do paciente — em construção (Fase 3)
      </p>
    </DashboardShell>
  );
}
