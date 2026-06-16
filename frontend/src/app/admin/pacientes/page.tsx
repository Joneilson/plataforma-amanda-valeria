"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { ApiError } from "@/lib/api";
import { formatCurrency } from "@/lib/format";
import { createPatient, listPatients, updatePatientStatus } from "@/lib/resources";
import type { Patient, PatientStatus } from "@/lib/types";
import {
  cardClass,
  compactButtonClass,
  errorBoxClass,
  inputClass,
  labelClass,
  successBoxClass,
} from "@/lib/ui";

const STATUS: PatientStatus[] = ["ATIVO", "INATIVO", "ALTA"];
const emptyForm = { nome: "", password: "", email: "", telefone: "", queixa_principal: "", valor_sessao: "" };

export default function PacientesPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [created, setCreated] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  function refresh() {
    listPatients(search).then(setPatients).catch(() => setError("Falha ao carregar pacientes."));
  }

  useEffect(refresh, [search]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      const patient = await createPatient({
        nome: form.nome,
        password: form.password,
        email: form.email || undefined,
        telefone: form.telefone,
        queixa_principal: form.queixa_principal,
        valor_sessao: form.valor_sessao ? Number(form.valor_sessao) : null,
      });
      setForm(emptyForm);
      setShowForm(false);
      setCreated(patient.user.username);
      refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Não foi possível cadastrar.");
    } finally {
      setSaving(false);
    }
  }

  async function changeStatus(p: Patient, status: PatientStatus) {
    await updatePatientStatus(p.id, status);
    refresh();
  }

  return (
    <DashboardShell role="PSICOLOGA">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl text-plum">Pacientes</h1>
        <button onClick={() => { setShowForm((v) => !v); setCreated(null); }} className={compactButtonClass}>
          {showForm ? "Cancelar" : "Novo paciente"}
        </button>
      </div>

      {created && (
        <p className={`${successBoxClass} mt-6`}>
          Paciente cadastrado. Login de acesso: <strong>{created}</strong> — informe ao paciente
          junto com a senha definida.
        </p>
      )}

      {showForm && (
        <form onSubmit={handleCreate} className={`mt-6 grid gap-4 p-6 sm:grid-cols-2 ${cardClass}`}>
          {error && <p className={`${errorBoxClass} sm:col-span-2`}>{error}</p>}
          <div>
            <label className={labelClass}>Nome completo *</label>
            <input required className={inputClass} value={form.nome}
              onChange={(e) => setForm({ ...form, nome: e.target.value })} />
          </div>
          <div>
            <label className={labelClass}>Senha inicial *</label>
            <input type="text" required className={inputClass} value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </div>
          <div>
            <label className={labelClass}>E-mail (opcional)</label>
            <input type="email" className={inputClass} value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </div>
          <div>
            <label className={labelClass}>Telefone</label>
            <input className={inputClass} value={form.telefone}
              onChange={(e) => setForm({ ...form, telefone: e.target.value })} />
          </div>
          <div>
            <label className={labelClass}>Valor da sessão (R$)</label>
            <input type="number" step="0.01" className={inputClass} value={form.valor_sessao}
              onChange={(e) => setForm({ ...form, valor_sessao: e.target.value })} />
          </div>
          <div>
            <label className={labelClass}>Queixa principal</label>
            <input className={inputClass} value={form.queixa_principal}
              onChange={(e) => setForm({ ...form, queixa_principal: e.target.value })} />
          </div>
          <div className="sm:col-span-2">
            <button type="submit" disabled={saving} className={compactButtonClass}>
              {saving ? "Salvando…" : "Cadastrar paciente"}
            </button>
            <p className="mt-2 text-xs text-ink/50">
              O login (nome.sobrenome) é gerado automaticamente.
            </p>
          </div>
        </form>
      )}

      <input className={`${inputClass} mt-6 max-w-xs`} placeholder="Buscar por nome…"
        value={search} onChange={(e) => setSearch(e.target.value)} />

      <div className={`mt-4 overflow-x-auto ${cardClass}`}>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-plum-200 text-left text-ink/60">
              <th className="px-4 py-3 font-medium">Nome</th>
              <th className="px-4 py-3 font-medium">Login</th>
              <th className="px-4 py-3 font-medium">Valor</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {patients.length === 0 ? (
              <tr><td colSpan={4} className="px-4 py-6 text-center text-ink/50">Nenhum paciente.</td></tr>
            ) : (
              patients.map((p) => (
                <tr key={p.id} className="border-b border-plum-200/50 transition-colors last:border-0 hover:bg-sand-light">
                  <td className="px-4 py-3 text-ink">{p.user.nome}</td>
                  <td className="px-4 py-3 font-mono text-xs text-ink/70">{p.user.username}</td>
                  <td className="px-4 py-3 text-ink/70">{formatCurrency(p.valor_sessao)}</td>
                  <td className="px-4 py-3">
                    <select value={p.status} onChange={(e) => changeStatus(p, e.target.value as PatientStatus)}
                      className="rounded-md border border-plum-200 bg-white px-2 py-1 text-sm shadow-sm">
                      {STATUS.map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </DashboardShell>
  );
}
