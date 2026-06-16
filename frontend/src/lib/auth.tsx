"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api } from "./api";
import { tokenStore } from "./auth-tokens";
import type { Role, User } from "./types";

interface RegisterPayload {
  nome: string;
  email: string;
  password: string;
  telefone?: string;
  accept_terms: boolean;
}

interface AuthData {
  access: string;
  refresh: string;
  user: User;
}

interface AuthState {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (payload: RegisterPayload) => Promise<User>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function homePathForRole(role: Role): string {
  return role === "PSICOLOGA" ? "/admin" : "/paciente";
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      if (tokenStore.access) {
        try {
          setUser(await api<User>("/me", {}, true));
        } catch {
          tokenStore.clear();
        }
      }
      setLoading(false);
    })();
  }, []);

  async function login(email: string, password: string) {
    const data = await api<AuthData>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    tokenStore.set(data.access, data.refresh);
    setUser(data.user);
    return data.user;
  }

  async function register(payload: RegisterPayload) {
    const data = await api<AuthData>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    tokenStore.set(data.access, data.refresh);
    setUser(data.user);
    return data.user;
  }

  async function logout() {
    try {
      if (tokenStore.refresh) {
        await api("/auth/logout", {
          method: "POST",
          body: JSON.stringify({ refresh: tokenStore.refresh }),
        }, true);
      }
    } catch {
      // logout é best-effort; segue limpando o cliente
    }
    tokenStore.clear();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth deve ser usado dentro de <AuthProvider>.");
  return ctx;
}
