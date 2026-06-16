"use client";

import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { homePathForRole, useAuth } from "@/lib/auth";
import type { Role } from "@/lib/types";

/** Protege uma área: exige login e, opcionalmente, um papel específico. */
export function RequireAuth({ role, children }: { role?: Role; children: ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.replace("/login");
    } else if (role && user.role !== role) {
      router.replace(homePathForRole(user.role));
    }
  }, [user, loading, role, router]);

  const blocked = loading || !user || (role !== undefined && user.role !== role);
  if (blocked) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-ink/60">
        Carregando…
      </div>
    );
  }
  return <>{children}</>;
}
