"use client";

import { useState, type ReactNode, type Ref } from "react";
import Link from "next/link";
import styles from "./auth.module.css";
import { PASSWORD_RULES } from "./validate";
import type { AuthCopy } from "@/lib/authCopy";

export function FlagIcon() {
  return (
    <svg viewBox="0 0 16 16" width="16" height="16" fill="none" aria-hidden>
      <path
        d="M4 14V2.5m0 0h7.5l-1.6 3 1.6 3H4"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function CheckIcon() {
  return (
    <svg viewBox="0 0 16 16" width="16" height="16" fill="none" aria-hidden>
      <path
        d="M3.5 8.5l3 3 6-7"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function Spinner() {
  return <span className={styles.spinner} aria-hidden />;
}

type FieldProps = {
  id: string;
  label: string;
  type?: string;
  value: string;
  onChange: (v: string) => void;
  onBlur?: () => void;
  error?: string | null;
  autoComplete?: string;
  inputRef?: Ref<HTMLInputElement>;
  describedBy?: string;
  disabled?: boolean;
  readOnly?: boolean;
  /** Extra content under the input, after any error (checklist, match note). */
  children?: ReactNode;
  /** Control placed at the right edge of the input (show/hide). */
  trailing?: ReactNode;
};

/** A labelled input with the product's flag treatment for errors. */
export function Field({
  id,
  label,
  type = "text",
  value,
  onChange,
  onBlur,
  error,
  autoComplete,
  inputRef,
  describedBy,
  disabled,
  readOnly,
  children,
  trailing,
}: FieldProps) {
  const errId = `${id}-error`;
  const described = [error ? errId : null, describedBy].filter(Boolean).join(" ") || undefined;
  return (
    <div className={styles.field}>
      <label htmlFor={id} className={styles.label}>
        {label}
      </label>
      <div className={`${styles.inputWrap} ${error ? styles.inputBad : ""}`}>
        <input
          id={id}
          ref={inputRef}
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onBlur={onBlur}
          autoComplete={autoComplete}
          aria-invalid={error ? true : undefined}
          aria-describedby={described}
          disabled={disabled}
          readOnly={readOnly}
          className={styles.input}
          spellCheck={false}
          autoCapitalize="none"
        />
        {trailing}
      </div>
      {error ? (
        <p id={errId} className={styles.error} role="alert">
          <span className={styles.mark}>
            <FlagIcon />
          </span>
          <span>{error}</span>
        </p>
      ) : null}
      {children}
    </div>
  );
}

/** Form-level failure (wrong password, rate limit...): same flag treatment as field errors. */
export function FormError({ children }: { children: ReactNode }) {
  return (
    <p className={styles.error} role="alert">
      <span className={styles.mark}>
        <FlagIcon />
      </span>
      <span>{children}</span>
    </p>
  );
}

type PasswordProps = Omit<FieldProps, "type" | "trailing"> & { copy: AuthCopy };

/** Password input with a Show / Hide toggle. */
export function PasswordField({ copy, ...rest }: PasswordProps) {
  const [shown, setShown] = useState(false);
  return (
    <Field
      {...rest}
      type={shown ? "text" : "password"}
      trailing={
        <button
          type="button"
          className={styles.toggle}
          onClick={() => setShown((s) => !s)}
          aria-pressed={shown}
          aria-controls={rest.id}
          disabled={rest.disabled}
        >
          {shown ? copy.hide : copy.show}
        </button>
      }
    />
  );
}

/** Live list of password rules; each flips to the all-clear treatment as it is met. */
export function PasswordChecklist({
  id,
  copy,
  checks,
}: {
  id: string;
  copy: AuthCopy;
  checks: boolean[];
}) {
  const labels = [copy.rule1, copy.rule2, copy.rule3, copy.rule4, copy.rule5];
  const count = checks.filter(Boolean).length;
  return (
    <div className={styles.rules} id={id}>
      <p className={styles.rulesHead}>
        <span>{copy.rulesTitle}</span>
        <span className={styles.rulesCount} aria-live="polite">
          {copy.rulesMet(count)}
        </span>
      </p>
      <ul className={styles.ruleList}>
        {PASSWORD_RULES.map((r, i) => (
          <li key={r.id} className={checks[i] ? styles.ruleMet : styles.ruleUnmet}>
            <span className={styles.ruleMark} aria-hidden>
              {checks[i] ? <CheckIcon /> : null}
            </span>
            <span>{labels[i]}</span>
            <span className="sr-only">{checks[i] ? copy.met : copy.notMet}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/** "Passwords match" in the same all-clear treatment as the chat's verification line. */
export function OkNote({ children }: { children: ReactNode }) {
  return (
    <p className={styles.ok} role="status">
      <span className={styles.mark}>
        <CheckIcon />
      </span>
      <span>{children}</span>
    </p>
  );
}

export function SubmitButton({
  busy,
  disabled,
  label,
  busyLabel,
  describedBy,
}: {
  busy: boolean;
  disabled?: boolean;
  label: string;
  busyLabel: string;
  describedBy?: string;
}) {
  return (
    <button
      type="submit"
      className={styles.submit}
      disabled={busy || disabled}
      aria-busy={busy}
      aria-describedby={describedBy}
    >
      {busy ? (
        <>
          <Spinner />
          <span>{busyLabel}</span>
        </>
      ) : (
        label
      )}
    </button>
  );
}

/** What the screen shows right before a real redirect would happen. */
export function SuccessPanel({
  title,
  body,
  actionLabel,
  href,
}: {
  title: string;
  body: string;
  actionLabel: string;
  href: string;
}) {
  return (
    <div className={styles.success} role="status">
      <p className={styles.successTitle}>
        <span className={styles.mark}>
          <CheckIcon />
        </span>
        {title}
      </p>
      <p className={styles.successBody}>{body}</p>
      <span className={styles.successBar} aria-hidden />
      <Link href={href} className={styles.successLink}>
        {actionLabel}
      </Link>
    </div>
  );
}

export function SwitchLine({
  prompt,
  linkLabel,
  href,
}: {
  prompt: string;
  linkLabel: string;
  href: string;
}) {
  return (
    <p className={styles.switch}>
      {prompt} <Link href={href}>{linkLabel}</Link>
    </p>
  );
}
