import { SITE } from "@/lib/site";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-sm rounded-2xl border border-plum-200 bg-white p-8 text-center">
        <h1 className="font-display text-3xl font-medium text-plum">{SITE.nome}</h1>
        <p className="mt-2 font-brand text-xs uppercase tracking-[0.3em] text-plum-600">
          Área de Atendimento
        </p>
        <p className="mt-8 text-sm text-ink/70">
          Tela de login (autenticação JWT) — implementada na Fase 1.
        </p>
      </div>
    </main>
  );
}
