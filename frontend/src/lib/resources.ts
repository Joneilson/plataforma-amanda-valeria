import { api } from "./api";
import type {
  AdminMetrics,
  Appointment,
  AppointmentStatus,
  Modalidade,
  Patient,
  PatientDashboard,
  PatientStatus,
} from "./types";

// ---- Dashboards ----
export const getAdminMetrics = () => api<AdminMetrics>("/dashboard/admin", {}, true);
export const getPatientDashboard = () => api<PatientDashboard>("/dashboard/patient", {}, true);

// ---- Pacientes ----
export interface CreatePatientPayload {
  nome: string;
  password: string;
  email?: string;
  telefone?: string;
  queixa_principal?: string;
  valor_sessao?: number | null;
  status?: PatientStatus;
}

export const listPatients = (search?: string) =>
  api<Patient[]>(
    `/patients${search ? `?search=${encodeURIComponent(search)}` : ""}`,
    {},
    true,
  );

export const createPatient = (payload: CreatePatientPayload) =>
  api<Patient>("/patients", { method: "POST", body: JSON.stringify(payload) }, true);

export const updatePatientStatus = (id: number, status: PatientStatus) =>
  api<Patient>(`/patients/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }, true);

// ---- Atendimentos ----
export interface CreateAppointmentPayload {
  patient: number;
  data_hora: string;
  duracao_min: number;
  modalidade: Modalidade;
  valor?: number | null;
  observacao?: string;
}

export const listAppointments = () => api<Appointment[]>("/appointments", {}, true);

export const createAppointment = (payload: CreateAppointmentPayload) =>
  api<Appointment>("/appointments", { method: "POST", body: JSON.stringify(payload) }, true);

export const setAppointmentStatus = (id: number, status: AppointmentStatus) =>
  api<Appointment>(`/appointments/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }, true);
