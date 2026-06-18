"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { ApiError } from "@/lib/api";
import { createNote, deleteNote, listNotes, updateNote } from "@/lib/resources";
import type { PatientNote } from "@/lib/types";
import {
  cardClass,
  compactButtonClass,
  errorBoxClass,
  inputClass,
  labelClass,
} from "@/lib/ui";

const emptyForm = { titulo: "", conteudo: "", compartilhar_com_psicologa: false };

function formatQuando(iso: string) {
  return new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function AnotacoesPage() {
  const [notes, setNotes] = useState<PatientNote[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  function load() {
    listNotes().then(setNotes).catch(() => setError("Falha ao carregar suas anotações."));
  }

  useEffect(load, []);

  function resetForm() {
    setForm(emptyForm);
    setEditingId(null);
    setError("");
  }

  function startEdit(n: PatientNote) {
    setError("");
    setEditingId(n.id);
    setForm({
      titulo: n.titulo,
      conteudo: n.conteudo,
      compartilhar_com_psicologa: n.compartilhar_com_psicologa,
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.conteudo.trim()) {
      setError("Escreva o conteúdo da anotação.");
      return;
    }
    setError("");
    setSaving(true);
    try {
      if (editingId === null) await createNote(form);
      else await updateNote(editingId, form);
      resetForm();
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Não foi possível salvar.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Excluir esta anotação? Esta ação não pode ser desfeita.")) return;
    try {
      await deleteNote(id);
      if (editingId === id) resetForm();
      load();
    } catch {
      setError("Não foi possível excluir.");
    }
  }

  return (
    <DashboardShell role="PACIENTE">
      <h1 className="font-display text-3xl text-plum">Minhas anotações</h1>
      <p className="mt-1 text-ink/60">
        Um espaço privado. Suas anotações são guardadas com segurança e só ficam visíveis para a
        psicóloga se você escolher compartilhar.
      </p>

      {/* Formulário (criar / editar) */}
      <form onSubmit={handleSubmit} className={`${cardClass} mt-6 p-6`}>
        <p className="font-brand text-xs uppercase tracking-[0.2em] text-plum-600">
          {editingId === null ? "Nova anotação" : "Editar anotação"}
        </p>

        <div className="mt-4">
          <label className={labelClass}>Título (opcional)</label>
          <input
            className={inputClass}
            value={form.titulo}
            maxLength={200}
            onChange={(e) => setForm({ ...form, titulo: e.target.value })}
          />
        </div>

        <div className="mt-4">
          <label className={labelClass}>Conteúdo *</label>
          <textarea
            className={`${inputClass} min-h-32 resize-y`}
            value={form.conteudo}
            onChange={(e) => setForm({ ...form, conteudo: e.target.value })}
            placeholder="Escreva o que quiser registrar…"
          />
        </div>

        <label className="mt-4 flex items-center gap-2 text-sm text-ink/70">
          <input
            type="checkbox"
            checked={form.compartilhar_com_psicologa}
            onChange={(e) => setForm({ ...form, compartilhar_com_psicologa: e.target.checked })}
            className="h-4 w-4 rounded border-plum-300 text-plum focus:ring-plum-200"
          />
          Compartilhar esta anotação com a psicóloga
        </label>

        {error && <p className={`${errorBoxClass} mt-4`}>{error}</p>}

        <div className="mt-5 flex items-center gap-3">
          <button type="submit" disabled={saving} className={compactButtonClass}>
            {saving ? "Salvando…" : editingId === null ? "Salvar anotação" : "Salvar alterações"}
          </button>
          {editingId !== null && (
            <button type="button" onClick={resetForm} className="text-sm text-ink/60 hover:text-ink">
              Cancelar edição
            </button>
          )}
        </div>
      </form>

      {/* Lista */}
      <div className="mt-6 space-y-3">
        {notes.length === 0 ? (
          <p className="text-center text-ink/50">Você ainda não tem anotações.</p>
        ) : (
          notes.map((n) => (
            <div key={n.id} className={`${cardClass} p-5`}>
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <p className="font-medium text-ink">{n.titulo || "Sem título"}</p>
                  <p className="mt-1 whitespace-pre-wrap text-sm text-ink/70">{n.conteudo}</p>
                </div>
                {n.compartilhar_com_psicologa && (
                  <span className="shrink-0 rounded-full bg-plum-200 px-2.5 py-1 text-xs text-plum">
                    Compartilhada
                  </span>
                )}
              </div>
              <div className="mt-3 flex items-center gap-4 text-sm">
                <span className="text-ink/40">{formatQuando(n.updated_at)}</span>
                <button onClick={() => startEdit(n)} className="font-medium text-plum hover:underline">
                  Editar
                </button>
                <button onClick={() => handleDelete(n.id)} className="text-danger hover:underline">
                  Excluir
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </DashboardShell>
  );
}
