"use client";

import Link from "next/link";
import { useState } from "react";
import { AuthCard } from "@/components/AuthCard";
import { api } from "@/lib/api";
import { errorBoxClass, inputClass, labelClass, primaryButtonClass, successBoxClass } from "@/lib/ui";

export default function RecuperarSenhaPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api("/auth/password-reset", { method: "POST", body: JSON.stringify({ email }) });
      setSent(true);
    } catch {
      setError("Não foi possível enviar agora. Tente novamente.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthCard titulo="Recuperar senha">
      {sent ? (
        <div className="space-y-6">
          <p className={successBoxClass}>
            Se este e-mail estiver cadastrado, enviamos as instruções para redefinir a senha.
            Verifique sua caixa de entrada.
          </p>
          <p className="text-center text-sm">
            <Link href="/login" className="text-plum hover:underline">Voltar ao login</Link>
          </p>
        </div>
      ) : (
        <>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && <p className={errorBoxClass}>{error}</p>}
            <div>
              <label className={labelClass} htmlFor="email">E-mail da conta</label>
              <input id="email" type="email" required autoComplete="email" className={inputClass}
                value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <button type="submit" disabled={loading} className={primaryButtonClass}>
              {loading ? "Enviando…" : "Enviar instruções"}
            </button>
          </form>
          <p className="mt-6 text-center text-sm">
            <Link href="/login" className="text-plum hover:underline">Voltar ao login</Link>
          </p>
        </>
      )}
    </AuthCard>
  );
}
