import type { AuthCopy } from "./authCopy";

type AuthErrLike = { code?: string; status?: number; message?: string } | null | undefined;

/** Maps a Supabase auth error to one of our plain-wording messages. Never exposes the raw server text. */
export function authErrorMessage(err: AuthErrLike, A: AuthCopy): string {
  const code = err?.code ?? "";
  const status = err?.status ?? 0;
  if (code === "invalid_credentials") return A.errInvalid;
  if (code === "email_not_confirmed") return A.errUnconfirmed;
  if (status === 429 || code.startsWith("over_")) return A.errRate;
  if (code === "user_already_exists" || code === "email_exists") return A.errExists;
  if (code === "weak_password") return A.errWeak;
  if (code === "signup_disabled" || code === "email_provider_disabled") return A.errSignupOff;
  return A.errGeneric;
}
