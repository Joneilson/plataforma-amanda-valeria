"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { ApiError } from "@/lib/api";
import {
  createHomework,
  deleteHomework,
  listHomework,
  listPatients,
} from "@/lib/resources";
import type { Homework, Patient } from "@/lib/types";
import {
  cardClass,
  compactButtonClass,
  errorBoxClass,
  inputClass,
  labelClass,
} from "@/lib/ui";

const emptyForm = { patient: "", titulo: "", descricao: "", prazo: "" };

function formatPrazo(iso: string | null) {
  if (!iso) return "—";
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
}

export default function TarefasAdminPage() {
  const [tasks, setTasks] = useState<Homework[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  function load() {
    listHomework().then(setTasks).catch(() => setError("Falha ao carregar as tarefas."));
  }

  useEffect(() => {
    load();
    listPatients().then(setPatients).catch(() => {});
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.patient || !form.titulo.trim()) {
      setError("Escolha o paciente e informe o título.");
      return;
    }
    setError("");
    setSaving(true);
    try {
      await createHomework({
        patient: Number(form.patient),
        titulo: form.titulo,
        descricao: form.descricao,
        prazo: form.prazo || null,
      });
      setForm(emptyForm);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Não foi possível criar a tarefa.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Excluir esta tarefa?")) return;
    try {
      await deleteHomework(id);
      load();
    } catch {
      setError("Não foi possível excluir.");
    }
  }

  return (
    <DashboardShell role="PSICOLOGA">
      <h1 className="font-display text-3xl text-plum">Tarefas terapêuticas</h1>
      <p className="mt-1 text-ink/60">Proponha atividades para os pacientes acompanharem.</p>

      {/* Nova tarefa */}
      <form onSubmit={handleSubmit} className={`${cardClass} mt-6 grid gap-4 p-6 sm:grid-cols-2`}>
        <div>
          <label className={labelClass}>Paciente *</label>
          <select
            className={inputClass}
            value={form.patient}
            onChange={(e) => setForm({ ...form, patient: e.target.value })}
          >
            <option value="">Selecione…</option>
            {patients.map((p) => (
              <option key={p.id} value={p.id}>
                {p.user.nome}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>Prazo (opcional)</label>
          <input
            type="date"
            className={inputClass}
            value={form.prazo}
            onChange={(e) => setForm({ ...form, prazo: e.target.value })}
          />
        </div>
        <div className="sm:col-span-2">
          <label className={labelClass}>Título *</label>
          <input
            className={inputClass}
            value={form.titulo}
            maxLength={200}
            onChange={(e) => setForm({ ...form, titulo: e.target.value })}
          />
        </div>
        <div className="sm:col-span-2">
          <label className={labelClass}>Descrição (opcional)</label>
          <textarea
            className={`${inputClass} min-h-24 resize-y`}
            value={form.descricao}
            onChange={(e) => setForm({ ...form, descricao: e.target.value })}
          />
        </div>
        {error && <p className={`${errorBoxClass} sm:col-span-2`}>{error}</p>}
        <div className="sm:col-span-2">
          <button type="submit" disabled={saving} className={compactButtonClass}>
            {saving ? "Criando…" : "Criar tarefa"}
          </button>
        </div>
      </form>

      {/* Lista */}
      <div className={`${cardClass} mt-6 overflow-hidden`}>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-plum-200 text-left text-ink/60">
              <th className="px-4 py-3 font-medium">Paciente</th>
              <th className="px-4 py-3 font-medium">Tarefa</th>
              <th className="px-4 py-3 font-medium">Prazo</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Ações</th>
            </tr>
          </thead>
          <tbody>
            {tasks.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-ink/50">
                  Nenhuma tarefa criada.
                </td>
              </tr>
            ) : (
              tasks.map((hw) => (
                <tr key={hw.id} className="border-b border-plum-200/50 last:border-0">
                  <td className="px-4 py-3 text-ink">{hw.patient_nome}</td>
                  <td className="px-4 py-3 text-ink/80">{hw.titulo}</td>
                  <td className="px-4 py-3 text-ink/60">{formatPrazo(hw.prazo)}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2.5 py-1 text-xs ${
                        hw.status === "CONCLUIDA"
                          ? "bg-success/15 text-[#4f5c4a]"
                          : "bg-plum-200 text-plum"
                      }`}
                    >
                      {hw.status === "CONCLUIDA" ? "Concluída" : "Pendente"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button onClick={() => handleDelete(hw.id)} className="text-danger hover:underline">
                      Excluir
                    </button>
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
