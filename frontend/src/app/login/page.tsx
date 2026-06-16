"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { AuthCard } from "@/components/AuthCard";
import { homePathForRole, useAuth } from "@/lib/auth";
import { errorBoxClass, inputClass, labelClass, primaryButtonClass } from "@/lib/ui";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const user = await login(username.trim(), password);
      router.replace(homePathForRole(user.role));
    } catch {
      setError("Usuário ou senha incorretos.");
      setLoading(false);
    }
  }

  return (
    <AuthCard titulo="Área de Atendimento">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <p className={errorBoxClass}>{error}</p>}
        <div>
          <label className={labelClass} htmlFor="username">Usuário</label>
          <input id="username" type="text" required autoComplete="username" className={inputClass}
            placeholder="nome.sobrenome" value={username}
            onChange={(e) => setUsername(e.target.value)} />
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

      <p className="mt-6 text-center text-xs text-ink/50">
        O acesso é criado pela psicóloga. Em caso de dúvida, entre em contato.
      </p>
    </AuthCard>
  );
}
