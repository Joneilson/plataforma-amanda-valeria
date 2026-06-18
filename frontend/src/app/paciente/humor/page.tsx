"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { ApiError } from "@/lib/api";
import { getMoodInsights, listMoodEntries, saveMood } from "@/lib/resources";
import type { MoodEntry, MoodInsights, MoodLevel } from "@/lib/types";
import {
  cardClass,
  compactButtonClass,
  errorBoxClass,
  inputClass,
  labelClass,
  successBoxClass,
} from "@/lib/ui";

const NIVEIS: { v: MoodLevel; emoji: string; label: string }[] = [
  { v: 1, emoji: "😣", label: "Muito ruim" },
  { v: 2, emoji: "😕", label: "Ruim" },
  { v: 3, emoji: "😐", label: "Neutro" },
  { v: 4, emoji: "🙂", label: "Bom" },
  { v: 5, emoji: "😄", label: "Ótimo" },
];

const EMOCOES = [
  "Ansioso",
  "Triste",
  "Calmo",
  "Feliz",
  "Cansado",
  "Irritado",
  "Motivado",
  "Grato",
];

const todayISO = (() => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(
    d.getDate(),
  ).padStart(2, "0")}`;
})();

function formatDia(iso: string) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("pt-BR", {
    weekday: "short",
    day: "2-digit",
    month: "short",
  });
}

const emojiFor = (n: MoodLevel) => NIVEIS.find((x) => x.v === n)?.emoji ?? "";

// Nível 1–5 mais próximo da média do dia (para o emoji da barra).
const roundLevel = (m: number) => Math.max(1, Math.min(5, Math.round(m))) as MoodLevel;

const formatHora = (iso: string) =>
  new Date(iso).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });

export default function HumorPage() {
  const [entries, setEntries] = useState<MoodEntry[]>([]);
  const [insights, setInsights] = useState<MoodInsights | null>(null);
  const [nivel, setNivel] = useState<MoodLevel | null>(null);
  const [emocoes, setEmocoes] = useState<string[]>([]);
  const [anotacao, setAnotacao] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [ok, setOk] = useState(false);

  function load() {
    listMoodEntries().then(setEntries).catch(() => setError("Falha ao carregar seu histórico."));
    getMoodInsights().then(setInsights).catch(() => {});
  }

  useEffect(load, []);

  // Pré-preenche com o registro de hoje, se já existir.
  useEffect(() => {
    const hoje = entries.find((e) => e.data === todayISO);
    if (hoje) {
      setNivel(hoje.nivel);
      setEmocoes(hoje.emocoes);
      setAnotacao(hoje.anotacao);
    }
  }, [entries]);

  const registrosHoje = entries.filter((e) => e.data === todayISO).length;

  function toggleEmocao(e: string) {
    setEmocoes((prev) => (prev.includes(e) ? prev.filter((x) => x !== e) : [...prev, e]));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (nivel === null) {
      setError("Escolha como você está se sentindo hoje.");
      return;
    }
    setError("");
    setOk(false);
    setSaving(true);
    try {
      await saveMood({ nivel, emocoes, anotacao, data: todayISO });
      setOk(true);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Não foi possível salvar.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <DashboardShell role="PACIENTE">
      <h1 className="font-display text-3xl text-plum">Humor diário</h1>
      <p className="mt-1 text-ink/60">
        Registre como você se sente. Suas anotações são privadas e guardadas com segurança.
      </p>

      {/* Registro de hoje */}
      <form onSubmit={handleSubmit} className={`${cardClass} mt-6 p-6`}>
        <p className="font-brand text-xs uppercase tracking-[0.2em] text-plum-600">
          Como você está agora?
        </p>
        {registrosHoje > 0 && (
          <p className="mt-1 text-sm text-ink/60">
            Você já registrou {registrosHoje}{" "}
            {registrosHoje === 1 ? "vez" : "vezes"} hoje. Pode registrar de novo — o humor do dia
            será a média.
          </p>
        )}

        <div className="mt-4 flex flex-wrap gap-3">
          {NIVEIS.map((n) => (
            <button
              key={n.v}
              type="button"
              onClick={() => setNivel(n.v)}
              className={`flex w-20 flex-col items-center gap-1 rounded-xl border px-3 py-3 transition ${
                nivel === n.v
                  ? "border-plum-400 bg-plum-200/60 shadow-sm"
                  : "border-plum-200 bg-white hover:bg-sand-light"
              }`}
            >
              <span className="text-3xl">{n.emoji}</span>
              <span className="text-center text-xs text-ink/70">{n.label}</span>
            </button>
          ))}
        </div>

        <div className="mt-5">
          <label className={labelClass}>Emoções (opcional)</label>
          <div className="flex flex-wrap gap-2">
            {EMOCOES.map((e) => (
              <button
                key={e}
                type="button"
                onClick={() => toggleEmocao(e)}
                className={`rounded-full border px-3 py-1 text-sm transition ${
                  emocoes.includes(e)
                    ? "border-plum-400 bg-plum text-sand-light"
                    : "border-plum-200 bg-white text-ink/70 hover:bg-sand-light"
                }`}
              >
                {e}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-5">
          <label className={labelClass}>Anotação (opcional)</label>
          <textarea
            className={`${inputClass} min-h-24 resize-y`}
            value={anotacao}
            onChange={(ev) => setAnotacao(ev.target.value)}
            placeholder="O que aconteceu hoje? Como foi o seu dia?"
          />
        </div>

        {error && <p className={`${errorBoxClass} mt-4`}>{error}</p>}
        {ok && <p className={`${successBoxClass} mt-4`}>Registro salvo. Até amanhã! 💜</p>}

        <button type="submit" disabled={saving} className={`${compactButtonClass} mt-5`}>
          {saving ? "Salvando…" : registrosHoje > 0 ? "Registrar atualização" : "Salvar"}
        </button>
      </form>

      {/* Insights */}
      {insights && insights.total_registros > 0 && (
        <div className={`${cardClass} mt-4 p-6`}>
          <div className="flex items-baseline justify-between">
            <p className="font-brand text-xs uppercase tracking-[0.2em] text-plum-600">
              Últimos {insights.dias} dias
            </p>
            <p className="text-sm text-ink/60">
              Média{" "}
              <span className="font-display text-xl text-plum">
                {insights.media?.toFixed(1) ?? "—"}
              </span>{" "}
              / 5
            </p>
          </div>
          <p className="mt-1 text-xs text-ink/40">
            Cada barra é a média do dia. Passe o mouse para ver as alterações daquele dia.
          </p>
          <div className="mt-6 flex items-end gap-1">
            {insights.serie.map((p) => (
              <div key={p.data} className="group relative flex flex-1 flex-col items-center gap-1">
                {/* Tooltip: alterações do dia */}
                <div className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 hidden w-52 -translate-x-1/2 rounded-lg border border-plum-200 bg-white p-3 text-left shadow-card group-hover:block">
                  <p className="text-xs font-medium capitalize text-plum">
                    {formatDia(p.data)} · média {p.media.toFixed(1)}
                  </p>
                  <ul className="mt-2 space-y-1.5">
                    {p.registros.map((r, i) => (
                      <li key={i} className="text-xs text-ink/70">
                        <span className="text-ink/50">{formatHora(r.hora)}</span>{" "}
                        <span className="mr-1">{emojiFor(r.nivel)}</span>
                        {r.nivel_display}
                        {r.emocoes.length > 0 && (
                          <span className="text-ink/45"> · {r.emocoes.join(", ")}</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
                <div
                  className="w-full max-w-3 rounded-t bg-plum-400 transition-colors group-hover:bg-plum"
                  style={{ height: `${p.media * 16}px` }}
                />
                <span className="text-[9px] text-ink/40">{emojiFor(roundLevel(p.media))}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Histórico */}
      <div className={`${cardClass} mt-4 overflow-hidden`}>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-plum-200 text-left text-ink/60">
              <th className="px-4 py-3 font-medium">Data</th>
              <th className="px-4 py-3 font-medium">Humor</th>
              <th className="px-4 py-3 font-medium">Emoções</th>
              <th className="px-4 py-3 font-medium">Anotação</th>
            </tr>
          </thead>
          <tbody>
            {entries.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-ink/50">
                  Nenhum registro ainda.
                </td>
              </tr>
            ) : (
              entries.map((e) => (
                <tr key={e.id} className="border-b border-plum-200/50 last:border-0">
                  <td className="px-4 py-3 text-ink/80">
                    <span className="capitalize">{formatDia(e.data)}</span>{" "}
                    <span className="text-ink/40">· {formatHora(e.created_at)}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="mr-1">{emojiFor(e.nivel)}</span>
                    <span className="text-ink/70">{e.nivel_display}</span>
                  </td>
                  <td className="px-4 py-3 text-ink/60">
                    {e.emocoes.length ? e.emocoes.join(", ") : <span className="text-ink/30">—</span>}
                  </td>
                  <td className="max-w-xs truncate px-4 py-3 text-ink/60" title={e.anotacao}>
                    {e.anotacao || <span className="text-ink/30">—</span>}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </DashboardShell>
  );
}
