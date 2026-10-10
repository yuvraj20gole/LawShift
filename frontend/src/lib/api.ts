import { createClient } from "@/lib/supabase/client";

/** The FastAPI service, called directly (same base the chat uses). */
export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://127.0.0.1:8000";

/** Client-side cap for chat and document API calls (below backend generation wait). */
export const CLIENT_FETCH_TIMEOUT_MS = 95_000;

export function fetchWithTimeout(
  input: RequestInfo | URL,
  init?: RequestInit,
  ms = CLIENT_FETCH_TIMEOUT_MS,
): Promise<Response> {
  const ctrl = new AbortController();
  const id = setTimeout(() => ctrl.abort(), ms);
  return fetch(input, { ...init, signal: ctrl.signal }).finally(() => clearTimeout(id));
}

/** `{ Authorization: "Bearer <token>" }` when a session exists, otherwise `{}`. */
export async function authHeaders(): Promise<Record<string, string>> {
  try {
    const { data } = await createClient().auth.getSession();
    const token = data.session?.access_token;
    return token ? { Authorization: `Bearer ${token}` } : {};
  } catch {
    return {};
  }
}
