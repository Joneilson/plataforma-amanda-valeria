"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import logoHorizontal from "@/assets/logo-horizontal.png";
import { useAuth } from "@/lib/auth";
import type { Role } from "@/lib/types";
import { RequireAuth } from "./RequireAuth";

interface NavItem {
  href: string;
  label: string;
  soon?: boolean;
}

const NAV: Record<Role, NavItem[]> = {
  PSICOLOGA: [
    { href: "/admin", label: "Dashboard" },
    { href: "/admin/pacientes", label: "Pacientes" },
    { href: "/admin/agenda", label: "Agenda" },
    { href: "#", label: "Bate-papo", soon: true },
    { href: "#", label: "Atendimento online", soon: true },
  ],
  PACIENTE: [
    { href: "/paciente", label: "Início" },
    { href: "/paciente/agenda", label: "Minha agenda" },
    { href: "#", label: "Humor diário", soon: true },
    { href: "#", label: "Anotações", soon: true },
    { href: "#", label: "Atendimento online", soon: true },
  ],
};

function Sidebar({ role }: { role: Role }) {
  const pathname = usePathname();
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-plum-200 bg-white px-4 py-6 md:flex">
      <Image src={logoHorizontal} alt="Amanda Valéria" priority className="mb-8 h-12 w-auto" />
      <nav className="flex flex-col gap-1">
        {NAV[role].map((item) =>
          item.soon ? (
            <span
              key={item.label}
              className="cursor-default rounded-lg px-3 py-2 text-sm text-ink/35"
              title="Em breve"
            >
              {item.label} <span className="text-[10px] uppercase tracking-wide">· em breve</span>
            </span>
          ) : (
            <Link
              key={item.href}
              href={item.href}
              className={`rounded-lg px-3 py-2 text-sm transition ${
                pathname === item.href
                  ? "bg-plum-200 font-medium text-plum"
                  : "text-ink/70 hover:bg-sand"
              }`}
            >
              {item.label}
            </Link>
          ),
        )}
      </nav>
    </aside>
  );
}

function TopBar() {
  const { user, logout } = useAuth();
  const router = useRouter();
  async function handleLogout() {
    await logout();
    router.replace("/login");
  }
  return (
    <header className="flex items-center justify-end gap-4 border-b border-plum-200 bg-white px-6 py-3">
      <span className="text-sm text-ink/70">{user?.nome}</span>
      <button
        onClick={handleLogout}
        className="rounded-full border border-plum-400 px-4 py-1.5 font-brand text-xs uppercase tracking-widest text-plum transition hover:bg-plum-200"
      >
        Sair
      </button>
    </header>
  );
}

export function DashboardShell({ role, children }: { role: Role; children: React.ReactNode }) {
  return (
    <RequireAuth role={role}>
      <div className="flex min-h-screen">
        <Sidebar role={role} />
        <div className="flex min-w-0 flex-1 flex-col">
          <TopBar />
          <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-8">{children}</main>
        </div>
      </div>
    </RequireAuth>
  );
}
