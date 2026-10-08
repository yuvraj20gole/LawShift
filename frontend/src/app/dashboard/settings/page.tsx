"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { usePrefs, type Lang } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { getAuthCopy } from "@/lib/authCopy";
import { authErrorMessage } from "@/lib/authErrors";
import { createClient } from "@/lib/supabase/client";
import { useSession } from "@/lib/useSession";
import { getDocCopy } from "@/lib/documentsCopy";
import { purgeUserFiles } from "@/lib/documents";
import { PageHead, Row } from "@/components/dashboard/DashParts";
import { Field, FormError, OkNote, PasswordChecklist, PasswordField, SubmitButton } from "@/components/auth/AuthParts";
import { passwordChecks } from "@/components/auth/validate";
import { FlagIcon } from "@/components/auth/AuthParts";
import styles from "@/components/dashboard/dashboard.module.css";

const LANGS: { code: Lang; label: string }[] = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिन्दी" },
  { code: "mr", label: "मराठी" },
];

export default function SettingsPage() {
  const { lang, setLang } = usePrefs();
  const router = useRouter();
  const C = getDashboardCopy(lang);
  const A = getAuthCopy(lang);
  const { email: sessionEmail } = useSession();
  const accountEmail = sessionEmail ?? "";

  const [pw, setPw] = useState("");
  const [cf, setCf] = useState("");
  const [status, setStatus] = useState<"idle" | "busy" | "done">("idle");
  const [pwFailure, setPwFailure] = useState<string | null>(null);

  const checks = passwordChecks(pw);
  const matches = cf.length > 0 && cf === pw;
  const valid = checks.every(Boolean) && matches;
  const confirmError = cf.length > 0 && cf !== pw ? A.mismatch : null;

  async function onPassword(e: FormEvent) {
    e.preventDefault();
    if (!valid || status === "busy") return;
    setStatus("busy");
    setPwFailure(null);
    try {
      const { error } = await createClient().auth.updateUser({ password: pw });
      if (error) {
        const code = (error as { code?: string }).code ?? "";
        setPwFailure(
          code === "same_password"
            ? A.errSamePassword
            : code === "reauthentication_needed" || code === "session_expired" || code === "session_not_found"
              ? A.errReauth
              : authErrorMessage(error, A),
        );
        setStatus("idle");
        return;
      }
      setPw("");
      setCf("");
      setStatus("done");
    } catch {
      setPwFailure(A.errGeneric);
      setStatus("idle");
    }
  }

  const [typed, setTyped] = useState("");
  const [deleting, setDeleting] = useState(false);
  const [deleteFailed, setDeleteFailed] = useState<"files" | "account" | null>(null);
  const DC = getDocCopy(lang);
  const canDelete = accountEmail !== "" && typed === accountEmail && !deleting;

  async function onDelete() {
    if (!canDelete) return;
    setDeleting(true);
    setDeleteFailed(null);
    try {
      await purgeUserFiles();
    } catch {
      setDeleteFailed("files");
      setDeleting(false);
      return;
    }
    try {
      const supabase = createClient();
      const { error } = await supabase.rpc("delete_my_account");
      if (error) throw error;
      await supabase.auth.signOut({ scope: "local" });
      router.replace("/?account=deleted");
      router.refresh();
    } catch {
      setDeleteFailed("account");
      setDeleting(false);
    }
  }

  return (
    <>
      <PageHead title={C.stTitle} lede={C.stLede} />

      <Row title={C.stEmailTitle}>
        <Field id="st-email" label={C.stEmailTitle} value={accountEmail} onChange={() => {}} readOnly />
        <p className={styles.note}>{C.stEmailNote}</p>
      </Row>

      <Row title={C.stLangTitle}>
        <div role="radiogroup" aria-label={C.stLangTitle} className={styles.segGroup}>
          {LANGS.map((l) => (
            <button
              key={l.code}
              type="button"
              role="radio"
              aria-checked={lang === l.code}
              className={lang === l.code ? styles.segOn : styles.seg}
              onClick={() => setLang(l.code)}
              lang={l.code}
            >
              {l.label}
            </button>
          ))}
        </div>
        <p className={styles.note}>{C.stLangNote}</p>
      </Row>

      <Row title={C.stPasswordTitle}>
        <form onSubmit={onPassword} noValidate className={styles.stack}>
          <PasswordField
            id="st-new"
            label={C.stNew}
            autoComplete="new-password"
            value={pw}
            onChange={(v) => {
              setPw(v);
              setStatus("idle");
            }}
            describedBy="st-rules"
            disabled={status === "busy"}
            copy={A}
          >
            <PasswordChecklist id="st-rules" copy={A} checks={checks} />
          </PasswordField>
          <PasswordField
            id="st-confirm"
            label={C.stConfirm}
            autoComplete="new-password"
            value={cf}
            onChange={setCf}
            error={confirmError}
            disabled={status === "busy"}
            copy={A}
          >
            {matches ? <OkNote>{A.matchOk}</OkNote> : null}
          </PasswordField>
          {pwFailure ? <FormError>{pwFailure}</FormError> : null}
          <SubmitButton busy={status === "busy"} disabled={!valid} label={C.stUpdate} busyLabel={C.stUpdating} />
          {status === "done" ? <OkNote>{C.stUpdated}</OkNote> : null}
        </form>
      </Row>

      <Row title={C.stDeleteTitle}>
        <div className={styles.danger}>
          <p className={styles.dangerTitle}>{C.stDeleteTitle}</p>
          <p className={styles.dangerBody}>{C.stDeleteBody}</p>
          <Field
            id="st-delete"
            label={C.stDeleteType(accountEmail)}
            value={typed}
            onChange={(v) => {
              setTyped(v);
              setDeleteFailed(null);
            }}
            autoComplete="off"
            disabled={deleting}
          />
          <button type="button" className={styles.dangerBtn} disabled={!canDelete} onClick={() => void onDelete()}>
            {C.stDeleteButton}
          </button>
          {deleteFailed ? (
            <p className={styles.flagNote} role="alert">
              <span className={styles.mark}>
                <FlagIcon />
              </span>
              {deleteFailed === "files" ? DC.stFilesFailed : C.stDeleteFailed}
            </p>
          ) : null}
        </div>
      </Row>
    </>
  );
}
