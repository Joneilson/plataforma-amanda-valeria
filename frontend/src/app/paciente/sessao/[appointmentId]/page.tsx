"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { DashboardShell } from "@/components/DashboardShell";
import { getVideoRoom } from "@/lib/resources";
import type { VideoRoom } from "@/lib/types";

export default function SessaoPacientePage() {
  const params = useParams();
  const router = useRouter();
  const appointmentId = Number(params.appointmentId);

  const [room, setRoom] = useState<VideoRoom | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getVideoRoom(appointmentId)
      .then(setRoom)
      .catch((err) => setError(err?.message ?? "Não foi possível entrar na sala."))
      .finally(() => setLoading(false));
  }, [appointmentId]);

  return (
    <DashboardShell role="PACIENTE">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-3xl text-plum">Minha sessão</h1>
        <button
          onClick={() => router.back()}
          className="rounded-full border border-plum-400 px-4 py-1.5 font-brand text-xs uppercase tracking-widest text-plum transition-all duration-200 hover:bg-plum-200"
        >
          Sair da sala
        </button>
      </div>

      {loading && (
        <p className="mt-10 text-center text-ink/60">Entrando na sala…</p>
      )}

      {error && (
        <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {room && (
        <div className="mt-6 overflow-hidden rounded-2xl border border-plum-200 bg-black shadow-soft">
          <iframe
            src={`${room.room_url}?t=${room.token}`}
            allow="camera; microphone; fullscreen; display-capture; autoplay"
            className="h-[calc(100vh-14rem)] w-full"
            style={{ border: "none" }}
          />
        </div>
      )}
    </DashboardShell>
  );
}
