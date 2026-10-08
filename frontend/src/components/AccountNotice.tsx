"use client";

import { useEffect, useState } from "react";
import { usePrefs } from "@/lib/prefs";
import { getAuthCopy } from "@/lib/authCopy";
import { CheckIcon } from "@/components/auth/AuthParts";
import styles from "./AccountNotice.module.css";

/** One-line all-clear shown once after an account is deleted (`/?account=deleted`). */
export function AccountNotice() {
  const { lang } = usePrefs();
  const [show, setShow] = useState(false);
  useEffect(() => {
    const url = new URL(window.location.href);
    if (url.searchParams.get("account") === "deleted") {
      setShow(true);
      url.searchParams.delete("account");
      window.history.replaceState(null, "", url.pathname + url.search + url.hash);
    }
  }, []);
  if (!show) return null;
  return (
    <p className={styles.notice} role="status">
      <CheckIcon />
      <span>{getAuthCopy(lang).accountDeleted}</span>
    </p>
  );
}
