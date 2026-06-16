import Image from "next/image";
import Link from "next/link";
import logoStacked from "@/assets/logo-stacked.png";
import { SITE } from "@/lib/site";

/** Moldura comum das telas de autenticação: logo + card centralizado. */
export function AuthCard({
  titulo,
  children,
}: {
  titulo: string;
  children: React.ReactNode;
}) {
  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <div className="w-full max-w-sm">
        <Link href="/" className="mx-auto mb-8 block w-40">
          <Image
            src={logoStacked}
            alt={`${SITE.nome} — ${SITE.profissao}`}
            priority
            className="mx-auto h-auto w-40"
          />
        </Link>
        <div className="rounded-2xl border border-plum-200 bg-white p-8">
          <h1 className="text-center font-brand text-xs uppercase tracking-[0.3em] text-plum-600">
            {titulo}
          </h1>
          <div className="mt-6">{children}</div>
        </div>
      </div>
    </main>
  );
}
