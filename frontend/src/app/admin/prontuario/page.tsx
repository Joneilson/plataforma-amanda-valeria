"use client";

import { useEffect, useRef, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import {
  createClinicalRecord,
  deleteClinicalRecord,
  listClinicalRecords,
  listPatients,
} from "@/lib/resources";
import type { ClinicalRecord, Patient } from "@/lib/types";
import {
  cardClass,
  compactButtonClass,
  errorBoxClass,
  inputClass,
  labelClass,
} from "@/lib/ui";

function formatData(iso: string) {
  return new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ProntuarioPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(null);
  const [records, setRecords] = useState<ClinicalRecord[]>([]);
  const [conteudo, setConteudo] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    listPatients().then(setPatients).catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedPatientId) return;
    setRecords([]);
    listClinicalRecords(selectedPatientId)
      .then(setRecords)
      .catch(() => setError("Falha ao carregar evoluções."));
  }, [selectedPatientId]);

  const selectedPatient = patients.find((p) => p.id === selectedPatientId);

  async function handleSave() {
    if (!selectedPatientId || !conteudo.trim()) return;
    setSaving(true);
    setError("");
    try {
      const record = await createClinicalRecord({
        patient: selectedPatientId,
        conteudo: conteudo.trim(),
      });
      setRecords((prev) => [record, ...prev]);
      setConteudo("");
      textareaRef.current?.focus();
    } catch {
      setError("Erro ao salvar evolução. Tente novamente.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Excluir esta evolução clínica? Esta ação não pode ser desfeita.")) return;
    try {
      await deleteClinicalRecord(id);
      setRecords((prev) => prev.filter((r) => r.id !== id));
    } catch {
      setError("Erro ao excluir evolução.");
    }
  }

  return (
    <DashboardShell role="PSICOLOGA">
      <h1 className="font-display text-3xl text-plum">Prontuário clínico</h1>
      <p className="mt-1 text-ink/60">
        Registros de evolução por sessão — visíveis apenas para você.
      </p>

      {/* Seleção de paciente */}
      <div className="mt-6 max-w-sm">
        <label className={labelClass}>Paciente</label>
        <select
          className={inputClass}
          value={selectedPatientId ?? ""}
          onChange={(e) =>
            setSelectedPatientId(e.target.value ? Number(e.target.value) : null)
          }
        >
          <option value="">Selecione um paciente…</option>
          {patients.map((p) => (
            <option key={p.id} value={p.id}>
              {p.user.nome}
            </option>
          ))}
        </select>
      </div>

      {selectedPatient && (
        <>
          {/* Formulário de nova evolução */}
          <div className={`${cardClass} mt-6 p-5`}>
            <h2 className="mb-3 font-semibold text-ink">
              Nova evolução — {selectedPatient.user.nome}
            </h2>
            {error && <p className={`${errorBoxClass} mb-3`}>{error}</p>}
            <textarea
              ref={textareaRef}
              className={`${inputClass} min-h-[140px] resize-y`}
              placeholder="Registre a evolução clínica desta sessão…"
              value={conteudo}
              onChange={(e) => setConteudo(e.target.value)}
            />
            <div className="mt-3 flex justify-end">
              <button
                className={compactButtonClass}
                onClick={handleSave}
                disabled={saving || !conteudo.trim()}
              >
                {saving ? "Salvando…" : "Salvar evolução"}
              </button>
            </div>
          </div>

          {/* Timeline de evoluções */}
          <div className="mt-6">
            <h2 className="mb-3 font-semibold text-ink">
              Histórico ({records.length} evolução{records.length !== 1 ? "ões" : ""})
            </h2>
            {records.length === 0 ? (
              <p className="text-center text-ink/50">Nenhuma evolução registrada ainda.</p>
            ) : (
              <ol className="relative border-l border-plum-200 pl-6 space-y-6">
                {records.map((r) => (
                  <li key={r.id} className="relative">
                    <span className="absolute -left-[1.4rem] top-1.5 h-3 w-3 rounded-full bg-plum ring-2 ring-white" />
                    <div className={`${cardClass} p-4`}>
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="text-xs text-plum-600 font-medium">
                            {formatData(r.created_at)}
                          </p>
                          {r.appointment_data && (
                            <p className="mt-0.5 text-xs text-ink/50">
                              Sessão de{" "}
                              {new Date(r.appointment_data.data_hora).toLocaleDateString("pt-BR")}
                            </p>
                          )}
                        </div>
                        <button
                          onClick={() => handleDelete(r.id)}
                          className="shrink-0 text-xs text-danger/70 hover:text-danger"
                        >
                          Excluir
                        </button>
                      </div>
                      <p className="mt-3 whitespace-pre-wrap text-sm text-ink/80 leading-relaxed">
                        {r.conteudo}
                      </p>
                    </div>
                  </li>
                ))}
              </ol>
            )}
          </div>
        </>
      )}
    </DashboardShell>
  );
}
