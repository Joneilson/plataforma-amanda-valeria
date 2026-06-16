import Image from "next/image";
import { SITE } from "@/lib/site";
import logoStacked from "@/assets/logo-stacked.png";

export default function Home() {
  return (
    <main className="min-h-screen">
      <section className="mx-auto flex max-w-5xl animate-fade-up flex-col items-center px-6 py-20 text-center">
        <h1 className="sr-only">
          {SITE.nome} — {SITE.profissao} ({SITE.crp})
        </h1>

        <Image
          src={logoStacked}
          alt={`${SITE.nome} — ${SITE.profissao}`}
          priority
          className="h-auto w-72 md:w-80"
        />

        <p className="mt-10 max-w-xl text-lg leading-relaxed text-ink/80">
          Um espaço de cuidado, escuta e acolhimento. Atendimento presencial em{" "}
          {SITE.endereco.cidade}/{SITE.endereco.estado} e online.
        </p>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <a
            href={SITE.whatsapp.link}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-full bg-plum px-8 py-3 font-brand text-sm uppercase tracking-widest text-sand-light shadow-sm transition-all duration-200 hover:bg-plum-600 hover:shadow-md active:scale-[0.98]"
          >
            Falar no WhatsApp
          </a>
          <a
            href="/login"
            className="rounded-full border border-plum-400 px-8 py-3 font-brand text-sm uppercase tracking-widest text-plum transition hover:bg-plum-200"
          >
            Área de Atendimento
          </a>
        </div>

        <footer className="mt-24 text-sm text-ink/60">
          <p>
            {SITE.endereco.local} — {SITE.endereco.rua}, {SITE.endereco.cidade}/
            {SITE.endereco.estado}
          </p>
          <p className="mt-1">
            <a href={SITE.instagram.link} className="hover:text-plum">
              {SITE.instagram.handle}
            </a>{" "}
            · {SITE.whatsapp.exibicao}
          </p>
        </footer>
      </section>
    </main>
  );
}
