"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { usePrefs, type Lang } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { getAuthCopy } from "@/lib/authCopy";
import { SAMPLE_EMAIL } from "@/lib/sampleData";
import { PageHead, Row } from "@/components/dashboard/DashParts";
import { Field, OkNote, PasswordChecklist, PasswordField, SubmitButton } from "@/components/auth/AuthParts";
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
  const C = getDashboardCopy(lang);
  const A = getAuthCopy(lang);

  const [cur, setCur] = useState("");
  const [pw, setPw] = useState("");
  const [cf, setCf] = useState("");
  const [status, setStatus] = useState<"idle" | "busy" | "done">("idle");
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => () => {
    if (timer.current) clearTimeout(timer.current);
  }, []);

  const checks = passwordChecks(pw);
  const matches = cf.length > 0 && cf === pw;
  const valid = cur.length > 0 && checks.every(Boolean) && matches;
  const confirmError = cf.length > 0 && cf !== pw ? A.mismatch : null;

  function onPassword(e: FormEvent) {
    e.preventDefault();
    if (!valid || status === "busy") return;
    setStatus("busy");
    timer.current = setTimeout(() => {
      setStatus("done");
      setCur("");
      setPw("");
      setCf("");
    }, 1400);
  }

  const [typed, setTyped] = useState("");
  const [deleted, setDeleted] = useState(false);
  const canDelete = typed === SAMPLE_EMAIL;

  return (
    <>
      <PageHead title={C.stTitle} lede={C.stLede} />

      <Row title={C.stEmailTitle}>
        <Field id="st-email" label={C.stEmailTitle} value={SAMPLE_EMAIL} onChange={() => {}} readOnly />
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
            id="st-current"
            label={C.stCurrent}
            autoComplete="current-password"
            value={cur}
            onChange={setCur}
            disabled={status === "busy"}
            copy={A}
          />
          <PasswordField
            id="st-new"
            label={C.stNew}
            autoComplete="new-password"
            value={pw}
            onChange={setPw}
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
            label={C.stDeleteType(SAMPLE_EMAIL)}
            value={typed}
            onChange={(v) => {
              setTyped(v);
              setDeleted(false);
            }}
            autoComplete="off"
          />
          <button type="button" className={styles.dangerBtn} disabled={!canDelete} onClick={() => setDeleted(true)}>
            {C.stDeleteButton}
          </button>
          {deleted ? (
            <p className={styles.flagNote} role="alert">
              <span className={styles.mark}>
                <FlagIcon />
              </span>
              {C.stDeleteDone}
            </p>
          ) : null}
        </div>
      </Row>
    </>
  );
}
