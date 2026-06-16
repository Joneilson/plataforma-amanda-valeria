import { tokenStore } from "./auth-tokens";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export class ApiError extends Error {
  status: number;
  data: unknown;
  constructor(status: number, data: unknown) {
    const detail =
      data && typeof data === "object" && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : `Erro ${status}`;
    super(detail);
    this.status = status;
    this.data = data;
  }
}

function buildHeaders(extra?: HeadersInit, token?: string | null): HeadersInit {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(extra as Record<string, string>),
  };
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function rawFetch(path: string, options: RequestInit, token?: string | null) {
  return fetch(`${API_URL}${path}`, {
    ...options,
    headers: buildHeaders(options.headers, token),
  });
}

async function tryRefresh(): Promise<string | null> {
  const refresh = tokenStore.refresh;
  if (!refresh) return null;
  const res = await rawFetch("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh }),
  });
  if (!res.ok) {
    tokenStore.clear();
    return null;
  }
  const data = (await res.json()) as { access?: string; refresh?: string };
  if (data.access && data.refresh) tokenStore.set(data.access, data.refresh);
  else if (data.access) tokenStore.setAccess(data.access);
  return data.access ?? null;
}

/**
 * Faz uma chamada à API. Com `auth = true`, injeta o access token e, em caso
 * de 401, tenta renovar via refresh token uma vez antes de desistir.
 */
export async function api<T = unknown>(
  path: string,
  options: RequestInit = {},
  auth = false,
): Promise<T> {
  let res = await rawFetch(path, options, auth ? tokenStore.access : null);

  if (res.status === 401 && auth) {
    const newAccess = await tryRefresh();
    if (newAccess) res = await rawFetch(path, options, newAccess);
  }

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;

  if (!res.ok) throw new ApiError(res.status, data);
  return data as T;
}
