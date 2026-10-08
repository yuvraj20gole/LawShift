"use client";

import { useRef, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { AuthShell } from "@/components/auth/AuthShell";
import {
  Field,
  FormError,
  OkNote,
  PasswordChecklist,
  PasswordField,
  SubmitButton,
  SuccessPanel,
  SwitchLine,
} from "@/components/auth/AuthParts";
import { isEmail, passwordChecks } from "@/components/auth/validate";
import { usePrefs } from "@/lib/prefs";
import { getAuthCopy } from "@/lib/authCopy";
import { authErrorMessage } from "@/lib/authErrors";
import { createClient } from "@/lib/supabase/client";
import styles from "@/components/auth/auth.module.css";

type Status = "idle" | "submitting" | "confirm";

export default function RegisterPage() {
  const { lang } = usePrefs();
  const router = useRouter();
  const A = getAuthCopy(lang);

  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [cf, setCf] = useState("");
  const [touched, setTouched] = useState({ email: false, cf: false });
  const [tried, setTried] = useState(false);
  const [status, setStatus] = useState<Status>("idle");

  const emailRef = useRef<HTMLInputElement>(null);
  const pwRef = useRef<HTMLInputElement>(null);
  const cfRef = useRef<HTMLInputElement>(null);
  const [failure, setFailure] = useState<string | null>(null);

  const checks = passwordChecks(pw);
  const rulesOk = checks.every(Boolean);
  const emailOk = isEmail(email);
  const matches = cf.length > 0 && cf === pw;
  const valid = emailOk && rulesOk && matches;

  const emailError =
    touched.email || tried
      ? email.trim() === ""
        ? A.emailRequired
        : !emailOk
          ? A.emailInvalid
          : null
      : null;
  const confirmError =
    cf.length > 0 && cf !== pw
      ? A.mismatch
      : (touched.cf || tried) && cf === ""
        ? A.confirmRequired
        : null;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (status !== "idle") return;
    if (!valid) {
      setTried(true);
      (!emailOk ? emailRef : !rulesOk ? pwRef : cfRef).current?.focus();
      return;
    }
    setStatus("submitting");
    setFailure(null);
    try {
      const { data, error } = await createClient().auth.signUp({
        email: email.trim(),
        password: pw,
        options: { emailRedirectTo: `${window.location.origin}/auth/callback` },
      });
      if (error) {
        setFailure(authErrorMessage(error, A));
        setStatus("idle");
        return;
      }
      // With email confirmation on, an already-registered address comes back as a
      // user with no identities (and no error), so the server does not leak who has an account.
      if (data.user && (data.user.identities?.length ?? 1) === 0) {
        setFailure(A.errExists);
        setStatus("idle");
        return;
      }
      if (!data.session) {
        setStatus("confirm");
        return;
      }
      router.replace("/dashboard/workspace");
      router.refresh();
    } catch {
      setFailure(A.errGeneric);
      setStatus("idle");
    }
  }

  const busy = status === "submitting";

  return (
    <AuthShell title={A.registerTitle} lede={A.registerLede}>
      {status === "confirm" ? (
        <SuccessPanel
          title={A.confirmTitle}
          body={A.confirmBody}
          actionLabel={A.backToLogin}
          href="/login"
        />
      ) : (
        <form onSubmit={onSubmit} noValidate className={styles.form}>
          <Field
            id="reg-email"
            label={A.emailLabel}
            type="email"
            autoComplete="email"
            value={email}
            onChange={setEmail}
            onBlur={() => setTouched((t) => ({ ...t, email: true }))}
            error={emailError}
            inputRef={emailRef}
            disabled={busy}
          />

          <PasswordField
            id="reg-password"
            label={A.passwordLabel}
            autoComplete="new-password"
            value={pw}
            onChange={setPw}
            inputRef={pwRef}
            describedBy="reg-rules"
            disabled={busy}
            copy={A}
          >
            <PasswordChecklist id="reg-rules" copy={A} checks={checks} />
          </PasswordField>

          <PasswordField
            id="reg-confirm"
            label={A.confirmLabel}
            autoComplete="new-password"
            value={cf}
            onChange={setCf}
            onBlur={() => setTouched((t) => ({ ...t, cf: true }))}
            error={confirmError}
            inputRef={cfRef}
            disabled={busy}
            copy={A}
          >
            {matches ? <OkNote>{A.matchOk}</OkNote> : null}
          </PasswordField>

          {failure ? <FormError>{failure}</FormError> : null}

          <SubmitButton
            busy={busy}
            disabled={!valid}
            label={A.createAccount}
            busyLabel={A.creating}
            describedBy={!valid ? "reg-hint" : undefined}
          />
          {!valid && !busy ? (
            <p id="reg-hint" className={styles.hint}>
              {A.disabledHint}
            </p>
          ) : null}
        </form>
      )}
      <p className={styles.hint}>{A.registerSavedNote}</p>
      <SwitchLine prompt={A.haveAccount} linkLabel={A.loginLink} href="/login" />
    </AuthShell>
  );
}
