"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { completeHomework, listHomework } from "@/lib/resources";
import type { Homework } from "@/lib/types";
import { cardClass } from "@/lib/ui";

function formatPrazo(iso: string | null) {
  if (!iso) return null;
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "short",
  });
}

function HomeworkCard({ hw, onToggle }: { hw: Homework; onToggle: (hw: Homework) => void }) {
  const concluida = hw.status === "CONCLUIDA";
  const prazo = formatPrazo(hw.prazo);
  return (
    <div className={`${cardClass} p-5 ${concluida ? "opacity-70" : ""}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className={`font-medium text-ink ${concluida ? "line-through" : ""}`}>{hw.titulo}</p>
          {hw.descricao && (
            <p className="mt-1 whitespace-pre-wrap text-sm text-ink/70">{hw.descricao}</p>
          )}
          <p className="mt-2 text-xs text-ink/40">
            {prazo ? `Prazo: ${prazo}` : "Sem prazo"} · por {hw.criado_por_nome}
          </p>
        </div>
        <button
          onClick={() => onToggle(hw)}
          className={`shrink-0 rounded-full px-3 py-1.5 text-sm font-medium transition ${
            concluida
              ? "border border-plum-200 text-ink/60 hover:bg-sand-light"
              : "bg-plum text-sand-light hover:bg-plum-600"
          }`}
        >
          {concluida ? "Reabrir" : "Concluir"}
        </button>
      </div>
    </div>
  );
}

export default function TarefasPacientePage() {
  const [tasks, setTasks] = useState<Homework[]>([]);
  const [error, setError] = useState("");

  function load() {
    listHomework().then(setTasks).catch(() => setError("Falha ao carregar suas tarefas."));
  }

  useEffect(load, []);

  async function toggle(hw: Homework) {
    try {
      await completeHomework(hw.id, hw.status !== "CONCLUIDA");
      load();
    } catch {
      setError("Não foi possível atualizar a tarefa.");
    }
  }

  const pendentes = tasks.filter((t) => t.status === "PENDENTE");
  const concluidas = tasks.filter((t) => t.status === "CONCLUIDA");

  return (
    <DashboardShell role="PACIENTE">
      <h1 className="font-display text-3xl text-plum">Minhas tarefas</h1>
      <p className="mt-1 text-ink/60">Atividades propostas pela sua psicóloga.</p>

      {error && <p className="mt-4 text-danger">{error}</p>}

      {tasks.length === 0 && !error && (
        <p className="mt-6 text-center text-ink/50">Você não tem tarefas no momento.</p>
      )}

      {pendentes.length > 0 && (
        <section className="mt-6">
          <p className="font-brand text-xs uppercase tracking-[0.2em] text-plum-600">
            Pendentes ({pendentes.length})
          </p>
          <div className="mt-3 space-y-3">
            {pendentes.map((hw) => (
              <HomeworkCard key={hw.id} hw={hw} onToggle={toggle} />
            ))}
          </div>
        </section>
      )}

      {concluidas.length > 0 && (
        <section className="mt-8">
          <p className="font-brand text-xs uppercase tracking-[0.2em] text-ink/40">
            Concluídas ({concluidas.length})
          </p>
          <div className="mt-3 space-y-3">
            {concluidas.map((hw) => (
              <HomeworkCard key={hw.id} hw={hw} onToggle={toggle} />
            ))}
          </div>
        </section>
      )}
    </DashboardShell>
  );
}
