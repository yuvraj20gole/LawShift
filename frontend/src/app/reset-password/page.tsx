"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { AuthShell } from "@/components/auth/AuthShell";
import {
  FormError,
  OkNote,
  PasswordChecklist,
  PasswordField,
  SubmitButton,
  SwitchLine,
} from "@/components/auth/AuthParts";
import { passwordChecks } from "@/components/auth/validate";
import { usePrefs } from "@/lib/prefs";
import { getAuthCopy } from "@/lib/authCopy";
import { authErrorMessage } from "@/lib/authErrors";
import { createClient } from "@/lib/supabase/client";
import styles from "@/components/auth/auth.module.css";

type Phase = "checking" | "ready" | "badLink" | "saving";

/**
 * Target of the Supabase reset email. The browser client exchanges the ?code= in the URL for a
 * short recovery session (it needs the PKCE verifier cookie set where the link was requested);
 * getSession() waits for that. No session means the link is expired, used, or from another browser.
 */
export default function ResetPasswordPage() {
  const { lang } = usePrefs();
  const router = useRouter();
  const A = getAuthCopy(lang);

  const [phase, setPhase] = useState<Phase>("checking");
  const [pw, setPw] = useState("");
  const [cf, setCf] = useState("");
  const [touchedCf, setTouchedCf] = useState(false);
  const [tried, setTried] = useState(false);
  const [failure, setFailure] = useState<string | null>(null);
  const pwRef = useRef<HTMLInputElement>(null);
  const cfRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let live = true;
    createClient()
      .auth.getSession()
      .then(({ data }) => {
        if (live) setPhase(data.session ? "ready" : "badLink");
      })
      .catch(() => {
        if (live) setPhase("badLink");
      });
    return () => {
      live = false;
    };
  }, []);

  const checks = passwordChecks(pw);
  const rulesOk = checks.every(Boolean);
  const matches = cf.length > 0 && cf === pw;
  const valid = rulesOk && matches;
  const confirmError =
    cf.length > 0 && cf !== pw ? A.mismatch : (touchedCf || tried) && cf === "" ? A.confirmRequired : null;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (phase !== "ready") return;
    if (!valid) {
      setTried(true);
      (!rulesOk ? pwRef : cfRef).current?.focus();
      return;
    }
    setPhase("saving");
    setFailure(null);
    try {
      const supabase = createClient();
      const { error } = await supabase.auth.updateUser({ password: pw });
      if (error) {
        setFailure(authErrorMessage(error, A));
        setPhase("ready");
        return;
      }
      // End the recovery session everywhere so the new password has to be used to log in.
      await supabase.auth.signOut({ scope: "global" }).catch(() => {});
      router.replace("/login?reset=1");
      router.refresh();
    } catch {
      setFailure(A.errGeneric);
      setPhase("ready");
    }
  }

  const busy = phase === "saving";

  return (
    <AuthShell title={A.resetTitle} lede={A.resetLede}>
      {phase === "checking" ? (
        <p className={styles.hint} role="status">
          {A.resetChecking}
        </p>
      ) : phase === "badLink" ? (
        <>
          <FormError>
            <strong>{A.resetLinkBadTitle}.</strong> {A.resetLinkBadBody}
          </FormError>
          <SwitchLine prompt="" linkLabel={A.requestNewLink} href="/forgot-password" />
        </>
      ) : (
        <form onSubmit={onSubmit} noValidate className={styles.form}>
          <PasswordField
            id="reset-password"
            label={A.newPasswordLabel}
            autoComplete="new-password"
            value={pw}
            onChange={setPw}
            inputRef={pwRef}
            describedBy="reset-rules"
            disabled={busy}
            copy={A}
          >
            <PasswordChecklist id="reset-rules" copy={A} checks={checks} />
          </PasswordField>

          <PasswordField
            id="reset-confirm"
            label={A.confirmLabel}
            autoComplete="new-password"
            value={cf}
            onChange={setCf}
            onBlur={() => setTouchedCf(true)}
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
            label={A.resetSubmit}
            busyLabel={A.resetSaving}
            describedBy={!valid ? "reset-hint" : undefined}
          />
          {!valid && !busy ? (
            <p id="reset-hint" className={styles.hint}>
              {A.disabledHint}
            </p>
          ) : null}
        </form>
      )}
    </AuthShell>
  );
}
