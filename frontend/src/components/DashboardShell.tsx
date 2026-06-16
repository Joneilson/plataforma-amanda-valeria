"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import logoHorizontal from "@/assets/logo-horizontal.png";
import { useAuth } from "@/lib/auth";
import type { Role } from "@/lib/types";
import { RequireAuth } from "./RequireAuth";

function TopBar() {
  const { user, logout } = useAuth();
  const router = useRouter();

  async function handleLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <header className="flex items-center justify-between border-b border-plum-200 bg-white px-6 py-3">
      <Image src={logoHorizontal} alt="Amanda Valéria" priority className="h-10 w-auto" />
      <div className="flex items-center gap-4">
        <span className="hidden text-sm text-ink/70 sm:inline">{user?.nome}</span>
        <button
          onClick={handleLogout}
          className="rounded-full border border-plum-400 px-4 py-1.5 font-brand text-xs uppercase tracking-widest text-plum transition hover:bg-plum-200"
        >
          Sair
        </button>
      </div>
    </header>
  );
}

export function DashboardShell({ role, children }: { role: Role; children: React.ReactNode }) {
  return (
    <RequireAuth role={role}>
      <div className="min-h-screen">
        <TopBar />
        <main className="mx-auto max-w-5xl px-6 py-10">{children}</main>
      </div>
    </RequireAuth>
  );
}
