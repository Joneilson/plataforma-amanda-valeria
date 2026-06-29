import { api } from "./api";
import type {
  AdminMetrics,
  Appointment,
  AppointmentStatus,
  ClinicalRecord,
  Conversation,
  Modalidade,
  Homework,
  Message,
  MoodEntry,
  MoodInsights,
  MoodLevel,
  Patient,
  PatientDashboard,
  PatientNote,
  PatientStatus,
  Payment,
  SharedNote,
  VideoRoom,
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

export interface UpdatePatientPayload {
  queixa_principal?: string;
  valor_sessao?: number | null;
  status?: PatientStatus;
}

export const updatePatient = (id: number, payload: UpdatePatientPayload) =>
  api<Patient>(`/patients/${id}`, { method: "PATCH", body: JSON.stringify(payload) }, true);

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

// ---- Humor diário ----
export interface SaveMoodPayload {
  nivel: MoodLevel;
  emocoes?: string[];
  anotacao?: string;
  data?: string;
}

export const listMoodEntries = () => api<MoodEntry[]>("/mood", {}, true);

export const saveMood = (payload: SaveMoodPayload) =>
  api<MoodEntry>("/mood", { method: "POST", body: JSON.stringify(payload) }, true);

export const getMoodInsights = (dias = 30) =>
  api<MoodInsights>(`/mood/insights?dias=${dias}`, {}, true);

// ---- Anotações pessoais ----
export interface SaveNotePayload {
  titulo?: string;
  conteudo: string;
  compartilhar_com_psicologa?: boolean;
}

export const listNotes = () => api<PatientNote[]>("/notes", {}, true);

export const createNote = (payload: SaveNotePayload) =>
  api<PatientNote>("/notes", { method: "POST", body: JSON.stringify(payload) }, true);

export const updateNote = (id: number, payload: SaveNotePayload) =>
  api<PatientNote>(`/notes/${id}`, { method: "PATCH", body: JSON.stringify(payload) }, true);

export const deleteNote = (id: number) =>
  api<void>(`/notes/${id}`, { method: "DELETE" }, true);

export const listSharedNotes = () => api<SharedNote[]>("/shared-notes", {}, true);

// ---- Tarefas terapêuticas ----
export interface CreateHomeworkPayload {
  patient: number;
  titulo: string;
  descricao?: string;
  prazo?: string | null;
}

export const listHomework = (patientId?: number) =>
  api<Homework[]>(`/homework${patientId ? `?patient=${patientId}` : ""}`, {}, true);

export const createHomework = (payload: CreateHomeworkPayload) =>
  api<Homework>("/homework", { method: "POST", body: JSON.stringify(payload) }, true);

export const deleteHomework = (id: number) =>
  api<void>(`/homework/${id}`, { method: "DELETE" }, true);

export const completeHomework = (id: number, concluida = true) =>
  api<Homework>(
    `/homework/${id}/concluir`,
    { method: "POST", body: JSON.stringify({ concluida }) },
    true,
  );

// ---- Prontuário clínico ----
export const listClinicalRecords = (patientId: number) =>
  api<ClinicalRecord[]>(`/clinical-records?patient=${patientId}`, {}, true);

export const createClinicalRecord = (payload: { patient: number; conteudo: string; appointment?: number | null }) =>
  api<ClinicalRecord>("/clinical-records", { method: "POST", body: JSON.stringify(payload) }, true);

export const updateClinicalRecord = (id: number, conteudo: string) =>
  api<ClinicalRecord>(`/clinical-records/${id}`, { method: "PATCH", body: JSON.stringify({ conteudo }) }, true);

export const deleteClinicalRecord = (id: number) =>
  api<void>(`/clinical-records/${id}`, { method: "DELETE" }, true);

// ---- Chat ----
export const listConversations = () => api<Conversation[]>("/conversations", {}, true);

export const listMessages = (patientId?: number) =>
  api<Message[]>(`/messages${patientId ? `?patient=${patientId}` : ""}`, {}, true);

export const sendMessage = (conteudo: string, patientId?: number) =>
  api<Message>(
    `/messages${patientId ? `?patient=${patientId}` : ""}`,
    { method: "POST", body: JSON.stringify({ conteudo }) },
    true,
  );

// ---- Vídeo ----
export const getVideoRoom = (appointmentId: number) =>
  api<VideoRoom>(`/video/rooms/${appointmentId}`, { method: "POST" }, true);

// ---- Pagamentos ----
export const createPayment = (appointmentId: number, metodo: "PIX" | "CARTAO" = "PIX") =>
  api<Payment>("/payments/checkout", { method: "POST", body: JSON.stringify({ appointment_id: appointmentId, metodo }) }, true);

/** @deprecated use createPayment */
export const createPixPayment = (appointmentId: number) => createPayment(appointmentId, "PIX");

export const listMyPayments = () =>
  api<Payment[]>("/payments/my", {}, true);

export const listAllPayments = () =>
  api<Payment[]>("/payments", {}, true);

export const markPaymentAsPaid = (paymentId: number) =>
  api<Payment>(`/payments/${paymentId}/marcar-pago`, { method: "POST" }, true);
