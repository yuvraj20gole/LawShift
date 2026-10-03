"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import Link from "next/link";
import { AuthShell } from "@/components/auth/AuthShell";
import { Field, SubmitButton, SuccessPanel } from "@/components/auth/AuthParts";
import { isEmail } from "@/components/auth/validate";
import { usePrefs } from "@/lib/prefs";
import { getAuthCopy } from "@/lib/authCopy";
import styles from "@/components/auth/auth.module.css";

export default function ForgotPasswordPage() {
  const { lang } = usePrefs();
  const A = getAuthCopy(lang);
  const [email, setEmail] = useState("");
  const [touched, setTouched] = useState(false);
  const [tried, setTried] = useState(false);
  const [status, setStatus] = useState<"idle" | "submitting" | "success">("idle");
  const emailRef = useRef<HTMLInputElement>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => {
    if (timer.current) clearTimeout(timer.current);
  }, []);

  const ok = isEmail(email);
  const error =
    touched || tried
      ? email.trim() === ""
        ? A.emailRequired
        : !ok
          ? A.emailInvalid
          : null
      : null;

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (status !== "idle") return;
    if (!ok) {
      setTried(true);
      emailRef.current?.focus();
      return;
    }
    setStatus("submitting");
    timer.current = setTimeout(() => setStatus("success"), 1400);
  }

  return (
    <AuthShell title={A.forgotTitle} lede={A.forgotLede}>
      {status === "success" ? (
        <SuccessPanel
          title={A.forgotSuccessTitle}
          body={A.forgotSuccessBody}
          actionLabel={A.backToLogin}
          href="/login"
        />
      ) : (
        <form onSubmit={onSubmit} noValidate className={styles.form}>
          <Field
            id="forgot-email"
            label={A.emailLabel}
            type="email"
            autoComplete="email"
            value={email}
            onChange={setEmail}
            onBlur={() => setTouched(true)}
            error={error}
            inputRef={emailRef}
            disabled={status === "submitting"}
          />
          <SubmitButton
            busy={status === "submitting"}
            label={A.sendLink}
            busyLabel={A.sending}
          />
        </form>
      )}
      <p className={styles.switch}>
        <Link href="/login">{A.backToLogin}</Link>
      </p>
    </AuthShell>
  );
}
