"use client";

import { useEffect, useRef, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { listMessages, sendMessage } from "@/lib/resources";
import { tokenStore } from "@/lib/auth-tokens";
import { api } from "@/lib/api";
import type { Conversation, Message } from "@/lib/types";
import { cardClass, inputClass } from "@/lib/ui";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

function formatHora(iso: string) {
  return new Date(iso).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

function formatDia(iso: string) {
  return new Date(iso).toLocaleDateString("pt-BR", {
    weekday: "short",
    day: "2-digit",
    month: "short",
  });
}

export default function ChatPacientePage() {
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState("");
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState("");
  const wsRef = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api<Conversation>("/my-conversation", {}, true)
      .then((conv) => {
        setConversation(conv);
        return listMessages();
      })
      .then(setMessages)
      .catch(() => setError("Falha ao carregar o chat."));
  }, []);

  useEffect(() => {
    if (!conversation) return;
    const token = tokenStore.access;
    const ws = new WebSocket(`${WS_BASE}/ws/chat/${conversation.id}/?token=${token}`);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setError("Erro de conexão. As mensagens serão enviadas mesmo assim.");
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data) as Message;
      setMessages((prev) => {
        // Evita duplicar mensagens próprias que já foram adicionadas via REST
        if (prev.some((m) => m.id === msg.id)) return prev;
        return [...prev, msg];
      });
    };

    return () => ws.close();
  }, [conversation]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    const conteudo = text.trim();
    if (!conteudo) return;
    setText("");

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ conteudo }));
    } else {
      try {
        const msg = await sendMessage(conteudo);
        setMessages((prev) => [...prev, msg]);
      } catch {
        setError("Falha ao enviar mensagem.");
        setText(conteudo);
      }
    }
  }

  let lastDay = "";

  return (
    <DashboardShell role="PACIENTE">
      <div className="flex items-baseline justify-between">
        <div>
          <h1 className="font-display text-3xl text-plum">Chat com a psicóloga</h1>
          <p className="mt-1 text-ink/60">
            Mensagens diretas com Amanda Valéria.{" "}
            <span className={connected ? "text-success font-medium" : "text-ink/40"}>
              {connected ? "● Online" : "○ Offline"}
            </span>
          </p>
        </div>
      </div>

      {error && <p className="mt-2 text-sm text-danger">{error}</p>}

      <div className={`${cardClass} mt-5 flex flex-col`} style={{ height: "64vh" }}>
        <div className="flex-1 overflow-y-auto p-4 space-y-1">
          {messages.length === 0 && (
            <p className="text-center text-ink/40 mt-10 text-sm">
              Nenhuma mensagem ainda. Diga olá!
            </p>
          )}
          {messages.map((m) => {
            const dia = formatDia(m.created_at);
            const showDivider = dia !== lastDay;
            lastDay = dia;
            const isMe = m.remetente_role === "PACIENTE";

            return (
              <div key={m.id}>
                {showDivider && (
                  <div className="flex items-center gap-2 my-4">
                    <hr className="flex-1 border-plum-100" />
                    <span className="text-xs text-ink/40 capitalize">{dia}</span>
                    <hr className="flex-1 border-plum-100" />
                  </div>
                )}
                <div className={`flex ${isMe ? "justify-end" : "justify-start"} mb-1`}>
                  <div
                    className={`max-w-[72%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                      isMe
                        ? "bg-plum text-white rounded-br-sm"
                        : "bg-plum-50 text-ink rounded-bl-sm"
                    }`}
                  >
                    {!isMe && (
                      <p className="text-[11px] font-medium text-plum-600 mb-1">
                        {m.remetente_nome}
                      </p>
                    )}
                    <p className="whitespace-pre-wrap">{m.conteudo}</p>
                    <p className={`mt-1 text-right text-[10px] ${isMe ? "text-white/60" : "text-ink/40"}`}>
                      {formatHora(m.created_at)}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
          <div ref={bottomRef} />
        </div>

        <div className="border-t border-plum-100 p-3 flex gap-2 items-end">
          <textarea
            className={`${inputClass} flex-1 resize-none`}
            rows={2}
            placeholder="Digite uma mensagem…"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <button
            onClick={handleSend}
            disabled={!text.trim()}
            className="rounded-full bg-plum px-5 py-2.5 text-sm text-white font-brand uppercase tracking-widest hover:bg-plum-600 disabled:opacity-50 transition-all shrink-0"
          >
            Enviar
          </button>
        </div>
      </div>
    </DashboardShell>
  );
}
