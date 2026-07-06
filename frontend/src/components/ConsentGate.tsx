"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { primaryButtonClass } from "@/lib/ui";

const CONSENT_INFO: Record<string, { titulo: string; descricao: string; anchor: string }> = {
  TERMOS_USO: {
    titulo: "Termos de uso",
    descricao: "Regras de utilização da plataforma.",
    anchor: "#termos",
  },
  PRIVACIDADE: {
    titulo: "Política de privacidade (LGPD)",
    descricao:
      "Como seus dados pessoais e de saúde são tratados, protegidos e por quanto tempo são guardados.",
    anchor: "#privacidade",
  },
  TELEATENDIMENTO: {
    titulo: "Consentimento de teleatendimento",
    descricao: "Condições do atendimento psicológico online (Resolução CFP).",
    anchor: "#teleatendimento",
  },
};

/**
 * Modal bloqueante exibido ao paciente enquanto houver consentimentos
 * pendentes (primeiro acesso ou nova versão dos termos). LGPD art. 7º/11.
 */
export function ConsentGate() {
  const [pendentes, setPendentes] = useState<string[]>([]);
  const [aceitos, setAceitos] = useState<Set<string>>(new Set());
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api<{ pendentes: string[] }>("/consents/pending", {}, true)
      .then((data) => setPendentes(data.pendentes))
      .catch(() => {});
  }, []);

  if (pendentes.length === 0) return null;

  const todosMarcados = pendentes.every((t) => aceitos.has(t));

  function toggle(tipo: string) {
    setAceitos((prev) => {
      const next = new Set(prev);
      if (next.has(tipo)) next.delete(tipo);
      else next.add(tipo);
      return next;
    });
  }

  async function confirmar() {
    setEnviando(true);
    setErro("");
    try {
      for (const tipo of pendentes) {
        await api("/consents", { method: "POST", body: JSON.stringify({ tipo }) }, true);
      }
      setPendentes([]);
    } catch {
      setErro("Não foi possível registrar o aceite. Tente novamente.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/50 p-4">
      <div className="w-full max-w-lg rounded-2xl border border-plum-200 bg-white p-6 shadow-card">
        <h2 className="font-display text-2xl text-plum">Antes de continuar</h2>
        <p className="mt-1 text-sm text-ink/70">
          Para usar a plataforma, precisamos do seu consentimento (Lei Geral de
          Proteção de Dados). Leia cada documento e marque as caixas.
        </p>

        <div className="mt-4 flex flex-col gap-3">
          {pendentes.map((tipo) => {
            const info = CONSENT_INFO[tipo];
            if (!info) return null;
            return (
              <label
                key={tipo}
                className="flex cursor-pointer items-start gap-3 rounded-lg border border-plum-200 p-3 transition hover:bg-sand"
              >
                <input
                  type="checkbox"
                  checked={aceitos.has(tipo)}
                  onChange={() => toggle(tipo)}
                  className="mt-1 h-4 w-4 accent-plum"
                />
                <span>
                  <span className="block text-sm font-medium text-ink">
                    Li e aceito os{" "}
                    <Link
                      href={`/privacidade${info.anchor}`}
                      target="_blank"
                      className="text-plum underline"
                    >
                      {info.titulo}
                    </Link>
                  </span>
                  <span className="block text-xs text-ink/60">{info.descricao}</span>
                </span>
              </label>
            );
          })}
        </div>

        {erro && <p className="mt-3 text-sm text-danger">{erro}</p>}

        <button
          onClick={confirmar}
          disabled={!todosMarcados || enviando}
          className={`${primaryButtonClass} mt-5`}
        >
          {enviando ? "Registrando…" : "Aceitar e continuar"}
        </button>
      </div>
    </div>
  );
}
