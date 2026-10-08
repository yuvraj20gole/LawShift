"use client";

import Link from "next/link";
import { AuthShell } from "@/components/auth/AuthShell";
import { usePrefs } from "@/lib/prefs";
import { getAuthCopy } from "@/lib/authCopy";
import styles from "@/components/auth/auth.module.css";

/** Labelled placeholder: password reset needs an email redirect page and Supabase URL settings that are not set up. */
export default function ForgotPasswordPage() {
  const { lang } = usePrefs();
  const A = getAuthCopy(lang);
  return (
    <AuthShell title={A.forgotTitle} lede={A.forgotLede}>
      <p className={styles.switch}>
        <Link href="/login">{A.backToLogin}</Link>
      </p>
    </AuthShell>
  );
}
