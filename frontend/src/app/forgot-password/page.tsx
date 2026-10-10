"use client";

import { useRef, useState, type FormEvent } from "react";
import { AuthShell } from "@/components/auth/AuthShell";
import { Field, FormError, SubmitButton, SuccessPanel, SwitchLine } from "@/components/auth/AuthParts";
import { isEmail } from "@/components/auth/validate";
import { usePrefs } from "@/lib/prefs";
import { getAuthCopy } from "@/lib/authCopy";
import { authErrorMessage } from "@/lib/authErrors";
import { createClient } from "@/lib/supabase/client";
import styles from "@/components/auth/auth.module.css";

type Status = "idle" | "sending" | "sent";

/**
 * Asks for the email and sends a Supabase reset link that lands on /reset-password.
 * The confirmation is identical whether or not the address has an account.
 */
export default function ForgotPasswordPage() {
  const { lang } = usePrefs();
  const A = getAuthCopy(lang);

  const [email, setEmail] = useState("");
  const [touched, setTouched] = useState(false);
  const [tried, setTried] = useState(false);
  const [status, setStatus] = useState<Status>("idle");
  const [failure, setFailure] = useState<string | null>(null);
  const emailRef = useRef<HTMLInputElement>(null);

  const emailOk = isEmail(email);
  const emailError =
    touched || tried ? (email.trim() === "" ? A.emailRequired : !emailOk ? A.emailInvalid : null) : null;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (status !== "idle") return;
    if (!emailOk) {
      setTried(true);
      emailRef.current?.focus();
      return;
    }
    setStatus("sending");
    setFailure(null);
    try {
      const { error } = await createClient().auth.resetPasswordForEmail(email.trim(), {
        redirectTo: `${window.location.origin}/reset-password`,
      });
      // Supabase does not report unknown addresses. Only rate limits and outages surface here,
      // and neither says anything about whether an account exists.
      if (error) {
        setFailure(authErrorMessage(error, A));
        setStatus("idle");
        return;
      }
      setStatus("sent");
    } catch {
      setFailure(A.errGeneric);
      setStatus("idle");
    }
  }

  const busy = status === "sending";

  return (
    <AuthShell title={A.forgotTitle} lede={A.forgotLede}>
      {status === "sent" ? (
        <SuccessPanel title={A.forgotSentTitle} body={A.forgotSentBody} actionLabel={A.backToLogin} href="/login" />
      ) : (
        <>
          <form onSubmit={onSubmit} noValidate className={styles.form}>
            <Field
              id="forgot-email"
              label={A.emailLabel}
              type="email"
              autoComplete="email"
              value={email}
              onChange={setEmail}
              onBlur={() => setTouched(true)}
              error={emailError}
              inputRef={emailRef}
              disabled={busy}
            />
            {failure ? <FormError>{failure}</FormError> : null}
            <SubmitButton busy={busy} label={A.forgotSend} busyLabel={A.forgotSending} />
          </form>
          <SwitchLine prompt="" linkLabel={A.backToLogin} href="/login" />
        </>
      )}
    </AuthShell>
  );
}
