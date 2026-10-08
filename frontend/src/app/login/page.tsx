"use client";

import { useRef, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AuthShell } from "@/components/auth/AuthShell";
import {
  Field,
  FormError,
  PasswordField,
  SubmitButton,
  SwitchLine,
} from "@/components/auth/AuthParts";
import { isEmail } from "@/components/auth/validate";
import { usePrefs } from "@/lib/prefs";
import { getAuthCopy } from "@/lib/authCopy";
import { authErrorMessage } from "@/lib/authErrors";
import { safeNext } from "@/lib/safeNext";
import { createClient } from "@/lib/supabase/client";
import styles from "@/components/auth/auth.module.css";

export default function LoginPage() {
  const { lang } = usePrefs();
  const router = useRouter();
  const A = getAuthCopy(lang);

  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [touched, setTouched] = useState({ email: false, pw: false });
  const [tried, setTried] = useState(false);
  const [busy, setBusy] = useState(false);
  const [failure, setFailure] = useState<string | null>(null);

  const emailRef = useRef<HTMLInputElement>(null);
  const pwRef = useRef<HTMLInputElement>(null);

  const emailOk = isEmail(email);
  // Any password is accepted here: this checks an existing account, so no strength rules.
  const emailError =
    touched.email || tried
      ? email.trim() === ""
        ? A.emailRequired
        : !emailOk
          ? A.emailInvalid
          : null
      : null;
  const pwError = (touched.pw || tried) && pw === "" ? A.passwordRequired : null;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (busy) return;
    if (!emailOk || pw === "") {
      setTried(true);
      (!emailOk ? emailRef : pwRef).current?.focus();
      return;
    }
    setBusy(true);
    setFailure(null);
    try {
      const { error } = await createClient().auth.signInWithPassword({
        email: email.trim(),
        password: pw,
      });
      if (error) {
        setFailure(authErrorMessage(error, A));
        setBusy(false);
        return;
      }
      const next = safeNext(new URLSearchParams(window.location.search).get("next"));
      router.replace(next ?? "/dashboard/workspace");
      router.refresh();
    } catch {
      setFailure(A.errGeneric);
      setBusy(false);
    }
  }

  return (
    <AuthShell title={A.loginTitle} lede={A.loginLede}>
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

        {failure ? <FormError>{failure}</FormError> : null}

        <SubmitButton busy={busy} label={A.logIn} busyLabel={A.loggingIn} />
      </form>
      <SwitchLine prompt={A.newHere} linkLabel={A.registerLink} href="/register" />
    </AuthShell>
  );
}
