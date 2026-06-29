"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DashboardShell } from "@/components/DashboardShell";
import { listConversations } from "@/lib/resources";
import type { Conversation } from "@/lib/types";
import { cardClass } from "@/lib/ui";

function formatQuando(iso: string) {
  const d = new Date(iso);
  const hoje = new Date();
  const ontem = new Date();
  ontem.setDate(hoje.getDate() - 1);

  if (d.toDateString() === hoje.toDateString()) {
    return d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  }
  if (d.toDateString() === ontem.toDateString()) {
    return "Ontem";
  }
  return d.toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
}

export default function AdminChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    listConversations()
      .then(setConversations)
      .catch(() => setError("Falha ao carregar conversas."));
  }, []);

  return (
    <DashboardShell role="PSICOLOGA">
      <h1 className="font-display text-3xl text-plum">Chat</h1>
      <p className="mt-1 text-ink/60">Conversas com os pacientes.</p>

      {error && <p className="mt-3 text-sm text-danger">{error}</p>}

      <div className="mt-6 space-y-2">
        {conversations.length === 0 && !error && (
          <p className="text-center text-ink/50">Nenhuma conversa iniciada ainda.</p>
        )}
        {conversations.map((c) => (
          <Link
            key={c.id}
            href={`/admin/chat/${c.patient_id}`}
            className={`${cardClass} flex items-center justify-between gap-4 p-4 hover:border-plum-300 transition-colors`}
          >
            <div className="flex items-center gap-3 min-w-0">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-plum-100 text-plum font-semibold text-sm uppercase">
                {c.patient_nome.charAt(0)}
              </div>
              <div className="min-w-0">
                <p className="font-medium text-ink truncate">{c.patient_nome}</p>
                {c.last_message && (
                  <p className="text-sm text-ink/50 truncate">
                    {c.last_message.conteudo}
                  </p>
                )}
              </div>
            </div>
            <div className="shrink-0 text-right">
              {c.last_message && (
                <p className="text-xs text-ink/40">{formatQuando(c.last_message.created_at)}</p>
              )}
              {c.unread_count > 0 && (
                <span className="mt-1 inline-flex h-5 w-5 items-center justify-center rounded-full bg-plum text-[11px] text-white font-semibold">
                  {c.unread_count}
                </span>
              )}
            </div>
          </Link>
        ))}
      </div>
    </DashboardShell>
  );
}
