"use client";

import { DashboardShell } from "@/components/DashboardShell";
import { cardClass } from "@/lib/ui";

const CONTATOS = [
  {
    nome: "CVV — Centro de Valorização da Vida",
    desc: "Apoio emocional e prevenção do suicídio, 24h, sigiloso e gratuito.",
    numero: "188",
    destaque: true,
  },
  { nome: "SAMU — Emergência médica", desc: "Atendimento de urgência.", numero: "192" },
  { nome: "Polícia Militar", desc: "Emergências e segurança.", numero: "190" },
  { nome: "Bombeiros", desc: "Resgate e emergências.", numero: "193" },
];

const RESPIRACAO = [
  "Inspire pelo nariz contando até 4.",
  "Segure o ar contando até 7.",
  "Solte lentamente pela boca contando até 8.",
  "Repita por 4 ciclos, com calma.",
];

export default function SosPage() {
  return (
    <DashboardShell role="PACIENTE">
      <h1 className="font-display text-3xl text-plum">Apoio em momentos difíceis</h1>
      <p className="mt-1 text-ink/60">
        Se você está passando por um momento de crise, você não está sozinho(a). Procure ajuda
        agora — falar com alguém pode aliviar.
      </p>

      {/* Contatos de emergência */}
      <div className="mt-6 space-y-3">
        {CONTATOS.map((c) => (
          <div
            key={c.numero}
            className={`${cardClass} flex items-center justify-between gap-4 p-5 ${
              c.destaque ? "border-plum-400 bg-plum-200/40" : ""
            }`}
          >
            <div className="min-w-0">
              <p className="font-medium text-ink">{c.nome}</p>
              <p className="mt-0.5 text-sm text-ink/60">{c.desc}</p>
            </div>
            <a
              href={`tel:${c.numero}`}
              className="shrink-0 rounded-full bg-plum px-5 py-2.5 font-brand text-sm uppercase tracking-widest text-sand-light shadow-sm transition hover:bg-plum-600"
            >
              Ligar {c.numero}
            </a>
          </div>
        ))}
      </div>

      {/* Exercício de respiração */}
      <div className={`${cardClass} mt-6 p-6`}>
        <p className="font-brand text-xs uppercase tracking-[0.2em] text-plum-600">
          Respiração para se acalmar (4-7-8)
        </p>
        <ol className="mt-3 list-decimal space-y-1.5 pl-5 text-sm text-ink/70">
          {RESPIRACAO.map((passo) => (
            <li key={passo}>{passo}</li>
          ))}
        </ol>
      </div>

      <p className="mt-6 text-center text-sm text-ink/50">
        Em caso de risco imediato à vida, ligue para o <strong>192</strong> (SAMU) ou vá ao
        pronto-socorro mais próximo.
      </p>
    </DashboardShell>
  );
}
