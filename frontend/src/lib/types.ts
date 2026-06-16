export type Role = "PACIENTE" | "PSICOLOGA";

export interface User {
  id: number;
  email: string;
  nome: string;
  telefone: string;
  role: Role;
}
