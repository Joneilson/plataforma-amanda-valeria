"use client";

import { useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { ApiError } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import {
  createAppointment,
  listAppointments,
  listPatients,
  setAppointmentStatus,
} from "@/lib/resources";
import type { Appointment, AppointmentStatus, Modalidade, Patient } from "@/lib/types";
import { compactButtonClass, errorBoxClass, inputClass, labelClass } from "@/lib/ui";

const STATUS: AppointmentStatus[] = ["AGENDADA", "CONFIRMADA", "REALIZADA", "FALTA", "CANCELADA"];

export default function AgendaPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    patient: "",
    data_hora: "",
    modalidade: "ONLINE" as Modalidade,
    duracao_min: "50",
    valor: "",
  });

  function refresh() {
    listAppointments().then(setAppointments).catch(() => setError("Falha ao carregar a agenda."));
  }

  useEffect(() => {
    refresh();
    listPatients().then(setPatients).catch(() => {});
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      await createAppointment({
        patient: Number(form.patient),
        data_hora: new Date(form.data_hora).toISOString(),
        duracao_min: Number(form.duracao_min),
        modalidade: form.modalidade,
        valor: form.valor ? Number(form.valor) : null,
      });
      setForm({ ...form, patient: "", data_hora: "", valor: "" });
      setShowForm(false);
      refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Não foi possível agendar.");
    } finally {
      setSaving(false);
    }
  }

  async function changeStatus(a: Appointment, status: AppointmentStatus) {
    await setAppointmentStatus(a.id, status);
    refresh();
  }

  return (
    <DashboardShell role="PSICOLOGA">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl text-plum">Agenda</h1>
        <button
          onClick={() => setShowForm((v) => !v)}
          disabled={patients.length === 0}
          className={compactButtonClass}
        >
          {showForm ? "Cancelar" : "Novo atendimento"}
        </button>
      </div>
      {patients.length === 0 && (
        <p className="mt-4 text-sm text-ink/60">Cadastre um paciente antes de agendar.</p>
      )}

      {showForm && (
        <form onSubmit={handleCreate} className="mt-6 grid gap-4 rounded-xl border border-plum-200 bg-white p-6 sm:grid-cols-2">
          {error && <p className={`${errorBoxClass} sm:col-span-2`}>{error}</p>}
          <div>
            <label className={labelClass}>Paciente</label>
            <select required className={inputClass} value={form.patient}
              onChange={(e) => setForm({ ...form, patient: e.target.value })}>
              <option value="">Selecione…</option>
              {patients.map((p) => <option key={p.id} value={p.id}>{p.user.nome}</option>)}
            </select>
          </div>
          <div>
            <label className={labelClass}>Data e hora</label>
            <input type="datetime-local" required className={inputClass} value={form.data_hora}
              onChange={(e) => setForm({ ...form, data_hora: e.target.value })} />
          </div>
          <div>
            <label className={labelClass}>Modalidade</label>
            <select className={inputClass} value={form.modalidade}
              onChange={(e) => setForm({ ...form, modalidade: e.target.value as Modalidade })}>
              <option value="ONLINE">Online</option>
              <option value="PRESENCIAL">Presencial</option>
            </select>
          </div>
          <div>
            <label className={labelClass}>Duração (min)</label>
            <input type="number" className={inputClass} value={form.duracao_min}
              onChange={(e) => setForm({ ...form, duracao_min: e.target.value })} />
          </div>
          <div className="sm:col-span-2">
            <button type="submit" disabled={saving} className={compactButtonClass}>
              {saving ? "Agendando…" : "Agendar"}
            </button>
          </div>
        </form>
      )}

      <div className="mt-6 overflow-x-auto rounded-xl border border-plum-200 bg-white">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-plum-200 text-left text-ink/60">
              <th className="px-4 py-3 font-medium">Paciente</th>
              <th className="px-4 py-3 font-medium">Data/hora</th>
              <th className="px-4 py-3 font-medium">Modalidade</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {appointments.length === 0 ? (
              <tr><td colSpan={4} className="px-4 py-6 text-center text-ink/50">Nenhum atendimento.</td></tr>
            ) : (
              appointments.map((a) => (
                <tr key={a.id} className="border-b border-plum-200/50 last:border-0">
                  <td className="px-4 py-3 text-ink">{a.patient_nome}</td>
                  <td className="px-4 py-3 text-ink/70">{formatDateTime(a.data_hora)}</td>
                  <td className="px-4 py-3 text-ink/70">{a.modalidade === "ONLINE" ? "Online" : "Presencial"}</td>
                  <td className="px-4 py-3">
                    <select value={a.status} onChange={(e) => changeStatus(a, e.target.value as AppointmentStatus)}
                      className="rounded-md border border-plum-200 bg-white px-2 py-1 text-sm">
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
