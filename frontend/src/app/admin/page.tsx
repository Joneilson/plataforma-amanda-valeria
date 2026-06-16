"use client";

import { DashboardShell } from "@/components/DashboardShell";
import { useAuth } from "@/lib/auth";

export default function AdminDashboard() {
  const { user } = useAuth();
  return (
    <DashboardShell role="PSICOLOGA">
      <h1 className="font-display text-4xl text-plum">Olá, {user?.nome?.split(" ")[0]}</h1>
      <p className="mt-3 text-ink/70">
        Painel de gestão. Em breve: métricas de atendimentos, agenda, pacientes,
        prontuários, bate-papo e sala de vídeo.
      </p>
      <p className="mt-6 font-brand text-xs uppercase tracking-widest text-plum-400">
        Painel da psicóloga — em construção (Fase 3)
      </p>
    </DashboardShell>
  );
}
