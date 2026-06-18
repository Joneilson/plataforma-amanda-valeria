"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { listSharedNotes } from "@/lib/resources";
import type { SharedNote } from "@/lib/types";
import { cardClass } from "@/lib/ui";

function formatQuando(iso: string) {
  return new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function AnotacoesCompartilhadasPage() {
  const [notes, setNotes] = useState<SharedNote[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    listSharedNotes()
      .then(setNotes)
      .catch(() => setError("Falha ao carregar as anotações."));
  }, []);

  return (
    <DashboardShell role="PSICOLOGA">
      <h1 className="font-display text-3xl text-plum">Anotações compartilhadas</h1>
      <p className="mt-1 text-ink/60">
        Anotações que os pacientes escolheram compartilhar com você.
      </p>

      {error && <p className="mt-4 text-danger">{error}</p>}

      <div className="mt-6 space-y-3">
        {notes.length === 0 ? (
          <p className="text-center text-ink/50">Nenhuma anotação compartilhada no momento.</p>
        ) : (
          notes.map((n) => (
            <div key={n.id} className={`${cardClass} p-5`}>
              <div className="flex items-baseline justify-between gap-4">
                <p className="font-medium text-ink">{n.titulo || "Sem título"}</p>
                <span className="shrink-0 text-sm text-plum-600">{n.patient_nome}</span>
              </div>
              <p className="mt-2 whitespace-pre-wrap text-sm text-ink/70">{n.conteudo}</p>
              <p className="mt-3 text-xs text-ink/40">{formatQuando(n.updated_at)}</p>
            </div>
          ))
        )}
      </div>
    </DashboardShell>
  );
}
