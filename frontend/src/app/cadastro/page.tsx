"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AuthCard } from "@/components/AuthCard";
import { ApiError } from "@/lib/api";
import { homePathForRole, useAuth } from "@/lib/auth";
import { errorBoxClass, inputClass, labelClass, primaryButtonClass } from "@/lib/ui";

export default function CadastroPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [form, setForm] = useState({ nome: "", email: "", telefone: "", password: "" });
  const [aceito, setAceito] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function update(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const user = await register({ ...form, accept_terms: aceito });
      router.replace(homePathForRole(user.role));
    } catch (err) {
      if (err instanceof ApiError && err.data && typeof err.data === "object") {
        const data = err.data as Record<string, string[] | string>;
        const first = Object.values(data)[0];
        setError(Array.isArray(first) ? first[0] : String(first));
      } else {
        setError("Não foi possível concluir o cadastro.");
      }
      setLoading(false);
    }
  }

  return (
    <AuthCard titulo="Criar conta">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <p className={errorBoxClass}>{error}</p>}
        <div>
          <label className={labelClass} htmlFor="nome">Nome completo</label>
          <input id="nome" required autoComplete="name" className={inputClass}
            value={form.nome} onChange={update("nome")} />
        </div>
        <div>
          <label className={labelClass} htmlFor="email">E-mail</label>
          <input id="email" type="email" required autoComplete="email" className={inputClass}
            value={form.email} onChange={update("email")} />
        </div>
        <div>
          <label className={labelClass} htmlFor="telefone">Telefone (WhatsApp)</label>
          <input id="telefone" type="tel" autoComplete="tel" className={inputClass}
            value={form.telefone} onChange={update("telefone")} />
        </div>
        <div>
          <label className={labelClass} htmlFor="password">Senha</label>
          <input id="password" type="password" required autoComplete="new-password" className={inputClass}
            value={form.password} onChange={update("password")} />
        </div>
        <label className="flex items-start gap-2 text-sm text-ink/70">
          <input type="checkbox" checked={aceito} onChange={(e) => setAceito(e.target.checked)}
            className="mt-1 accent-plum" />
          <span>Li e aceito os termos de uso e a política de privacidade (LGPD).</span>
        </label>
        <button type="submit" disabled={loading} className={primaryButtonClass}>
          {loading ? "Criando…" : "Criar conta"}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-ink/70">
        Já tem conta?{" "}
        <Link href="/login" className="text-plum hover:underline">Entrar</Link>
      </p>
    </AuthCard>
  );
}
