"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AuthShell } from "@/components/auth/AuthShell";
import {
  Field,
  PasswordField,
  SubmitButton,
  SuccessPanel,
  SwitchLine,
} from "@/components/auth/AuthParts";
import { isEmail } from "@/components/auth/validate";
import { usePrefs } from "@/lib/prefs";
import { getAuthCopy } from "@/lib/authCopy";
import styles from "@/components/auth/auth.module.css";

type Status = "idle" | "submitting" | "success";

export default function LoginPage() {
  const { lang } = usePrefs();
  const router = useRouter();
  const A = getAuthCopy(lang);

  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [touched, setTouched] = useState({ email: false, pw: false });
  const [tried, setTried] = useState(false);
  const [status, setStatus] = useState<Status>("idle");

  const emailRef = useRef<HTMLInputElement>(null);
  const pwRef = useRef<HTMLInputElement>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => {
    if (timer.current) clearTimeout(timer.current);
  }, []);

  const emailOk = isEmail(email);
  // Any password is accepted: this checks an existing account, so no strength rules.
  const emailError =
    touched.email || tried
      ? email.trim() === ""
        ? A.emailRequired
        : !emailOk
          ? A.emailInvalid
          : null
      : null;
  const pwError = (touched.pw || tried) && pw === "" ? A.passwordRequired : null;

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (status !== "idle") return;
    if (!emailOk || pw === "") {
      setTried(true);
      (!emailOk ? emailRef : pwRef).current?.focus();
      return;
    }
    setStatus("submitting");
    // Placeholder: the real sign-in call is wired in a separate pass.
    timer.current = setTimeout(() => {
      setStatus("success");
      // Let the success panel and its progress rule play, then go to the account area.
      timer.current = setTimeout(() => router.push("/dashboard"), 1800);
    }, 1600);
  }

  const busy = status === "submitting";

  return (
    <AuthShell title={A.loginTitle} lede={A.loginLede}>
      {status === "success" ? (
        <SuccessPanel
          title={A.loginSuccessTitle}
          body={A.successBody}
          actionLabel={A.continueTo}
          href="/dashboard"
        />
      ) : (
        <form onSubmit={onSubmit} noValidate className={styles.form}>
          <Field
            id="login-email"
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
            id="login-password"
            label={A.passwordLabel}
            autoComplete="current-password"
            value={pw}
            onChange={setPw}
            onBlur={() => setTouched((t) => ({ ...t, pw: true }))}
            error={pwError}
            inputRef={pwRef}
            disabled={busy}
            copy={A}
          >
            <p className={styles.forgotRow}>
              <Link href="/forgot-password">{A.forgot}</Link>
            </p>
          </PasswordField>

          <SubmitButton
            busy={busy}
            label={A.logIn}
            busyLabel={A.loggingIn}
          />
        </form>
      )}
      <SwitchLine prompt={A.newHere} linkLabel={A.registerLink} href="/register" />
    </AuthShell>
  );
}
