"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { AuthCard } from "@/components/AuthCard";
import { ApiError, api } from "@/lib/api";
import { errorBoxClass, inputClass, labelClass, primaryButtonClass, successBoxClass } from "@/lib/ui";

function RedefinirForm() {
  const params = useSearchParams();
  const router = useRouter();
  const uid = params.get("uid") ?? "";
  const token = params.get("token") ?? "";

  const [password, setPassword] = useState("");
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const linkInvalido = !uid || !token;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api("/auth/password-reset/confirm", {
        method: "POST",
        body: JSON.stringify({ uid, token, new_password: password }),
      });
      setDone(true);
      setTimeout(() => router.replace("/login"), 2000);
    } catch (err) {
      if (err instanceof ApiError && err.status === 400) {
        setError("Link inválido ou expirado. Solicite um novo.");
      } else {
        setError("Não foi possível redefinir a senha.");
      }
      setLoading(false);
    }
  }

  if (linkInvalido) {
    return (
      <div className="space-y-6">
        <p className={errorBoxClass}>Link inválido. Solicite uma nova redefinição.</p>
        <p className="text-center text-sm">
          <Link href="/recuperar-senha" className="text-plum hover:underline">Recuperar senha</Link>
        </p>
      </div>
    );
  }

  if (done) {
    return (
      <p className={successBoxClass}>Senha redefinida com sucesso! Redirecionando para o login…</p>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <p className={errorBoxClass}>{error}</p>}
      <div>
        <label className={labelClass} htmlFor="password">Nova senha</label>
        <input id="password" type="password" required autoComplete="new-password" className={inputClass}
          value={password} onChange={(e) => setPassword(e.target.value)} />
      </div>
      <button type="submit" disabled={loading} className={primaryButtonClass}>
        {loading ? "Salvando…" : "Redefinir senha"}
      </button>
    </form>
  );
}

export default function RedefinirSenhaPage() {
  return (
    <AuthCard titulo="Redefinir senha">
      <Suspense fallback={<p className="text-center text-sm text-ink/60">Carregando…</p>}>
        <RedefinirForm />
      </Suspense>
    </AuthCard>
  );
}
