"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DashboardShell } from "@/components/DashboardShell";
import { formatDateTime } from "@/lib/format";
import { listAppointments } from "@/lib/resources";
import type { Appointment } from "@/lib/types";

function isUpcoming(dataHora: string) {
  const diff = new Date(dataHora).getTime() - Date.now();
  return diff > -30 * 60 * 1000 && diff < 2 * 60 * 60 * 1000;
}

const STATUS_LABEL: Record<string, string> = {
  AGENDADA: "Agendada",
  CONFIRMADA: "Confirmada",
  REALIZADA: "Realizada",
  FALTA: "Falta",
  CANCELADA: "Cancelada",
};

export default function PacienteAgenda() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);

  useEffect(() => {
    listAppointments().then(setAppointments).catch(() => {});
  }, []);

  return (
    <DashboardShell role="PACIENTE">
      <h1 className="font-display text-3xl text-plum">Minha agenda</h1>

      <div className="mt-6 overflow-x-auto rounded-xl border border-plum-200 bg-white shadow-soft">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-plum-200 text-left text-ink/60">
              <th className="px-4 py-3 font-medium">Data/hora</th>
              <th className="px-4 py-3 font-medium">Modalidade</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {appointments.length === 0 ? (
              <tr><td colSpan={4} className="px-4 py-6 text-center text-ink/50">Nenhum atendimento.</td></tr>
            ) : (
              appointments.map((a) => (
                <tr key={a.id} className="border-b border-plum-200/50 transition-colors last:border-0 hover:bg-sand-light">
                  <td className="px-4 py-3 text-ink">{formatDateTime(a.data_hora)}</td>
                  <td className="px-4 py-3 text-ink/70">{a.modalidade === "ONLINE" ? "Online" : "Presencial"}</td>
                  <td className="px-4 py-3 text-ink/70">{STATUS_LABEL[a.status]}</td>
                  <td className="px-4 py-3">
                    {a.modalidade === "ONLINE" && isUpcoming(a.data_hora) && (
                      <Link
                        href={`/paciente/sessao/${a.id}`}
                        className="rounded-full bg-plum px-3 py-1 text-xs font-medium text-white transition-opacity hover:opacity-80"
                      >
                        Entrar na sala
                      </Link>
                    )}
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
