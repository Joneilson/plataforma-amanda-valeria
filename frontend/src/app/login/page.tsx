"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AuthCard } from "@/components/AuthCard";
import { homePathForRole, useAuth } from "@/lib/auth";
import { errorBoxClass, inputClass, labelClass, primaryButtonClass } from "@/lib/ui";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const user = await login(email, password);
      router.replace(homePathForRole(user.role));
    } catch {
      setError("E-mail ou senha incorretos.");
      setLoading(false);
    }
  }

  return (
    <AuthCard titulo="Área de Atendimento">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <p className={errorBoxClass}>{error}</p>}
        <div>
          <label className={labelClass} htmlFor="email">E-mail</label>
          <input id="email" type="email" required autoComplete="email" className={inputClass}
            value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div>
          <label className={labelClass} htmlFor="password">Senha</label>
          <input id="password" type="password" required autoComplete="current-password" className={inputClass}
            value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <button type="submit" disabled={loading} className={primaryButtonClass}>
          {loading ? "Entrando…" : "Entrar"}
        </button>
      </form>

      <div className="mt-6 space-y-2 text-center text-sm text-ink/70">
        <p>
          <Link href="/recuperar-senha" className="hover:text-plum">Esqueci minha senha</Link>
        </p>
        <p>
          Não tem conta?{" "}
          <Link href="/cadastro" className="text-plum hover:underline">Criar conta</Link>
        </p>
      </div>
    </AuthCard>
  );
}
