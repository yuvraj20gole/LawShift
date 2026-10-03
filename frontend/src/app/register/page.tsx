"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { AuthShell } from "@/components/auth/AuthShell";
import {
  Field,
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
import styles from "@/components/auth/auth.module.css";

type Status = "idle" | "submitting" | "success";

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
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => {
    if (timer.current) clearTimeout(timer.current);
  }, []);

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

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (status !== "idle") return;
    if (!valid) {
      setTried(true);
      (!emailOk ? emailRef : !rulesOk ? pwRef : cfRef).current?.focus();
      return;
    }
    setStatus("submitting");
    // Placeholder: the real sign-up call is wired in a separate pass.
    timer.current = setTimeout(() => {
      setStatus("success");
      // Let the success panel and its progress rule play, then go to the account area.
      timer.current = setTimeout(() => router.push("/dashboard"), 1800);
    }, 1600);
  }

  const busy = status === "submitting";

  return (
    <AuthShell title={A.registerTitle} lede={A.registerLede}>
      {status === "success" ? (
        <SuccessPanel
          title={A.registerSuccessTitle}
          body={A.successBody}
          actionLabel={A.continueTo}
          href="/dashboard"
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
      <SwitchLine prompt={A.haveAccount} linkLabel={A.loginLink} href="/login" />
    </AuthShell>
  );
}
