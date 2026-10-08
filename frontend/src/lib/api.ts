import { createClient } from "@/lib/supabase/client";

/** The FastAPI service, called directly (same base the chat uses). */
export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://127.0.0.1:8000";

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
