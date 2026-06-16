export type Role = "PACIENTE" | "PSICOLOGA";

export interface User {
  id: number;
  username: string;
  email: string | null;
  nome: string;
  telefone: string;
  role: Role;
}

export type PatientStatus = "ATIVO" | "INATIVO" | "ALTA";
export type Modalidade = "ONLINE" | "PRESENCIAL";
export type AppointmentStatus =
  | "AGENDADA"
  | "CONFIRMADA"
  | "REALIZADA"
  | "FALTA"
  | "CANCELADA";

export interface Patient {
  id: number;
  user: User;
  data_nascimento: string | null;
  genero: string;
  queixa_principal: string;
  contato_emergencia_nome: string;
  contato_emergencia_telefone: string;
  status: PatientStatus;
  inicio_tratamento: string;
  valor_sessao: string | null;
  created_at: string;
}

export interface Appointment {
  id: number;
  patient: number;
  patient_nome: string;
  data_hora: string;
  duracao_min: number;
  modalidade: Modalidade;
  status: AppointmentStatus;
  valor: string | null;
  observacao: string;
  created_at: string;
}

export interface AdminMetrics {
  atendimentos_realizados: number;
  horas_atendidas: number;
  online: number;
  presencial: number;
  faltas: number;
  pacientes_ativos: number;
  proximos_7_dias: number;
}

export interface PatientDashboard {
  proximo_atendimento: Appointment | null;
  sessoes_realizadas: number;
}
