"use client";

import Link from "next/link";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { PageHead } from "./DashParts";
import styles from "./dashboard.module.css";

/** A plain "coming next" page: says what the page will do and shows nothing else. */
export function ComingNext({ which }: { which: "mapping" | "rulings" }) {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  const title = which === "mapping" ? C.mapTitle : C.rulTitle;
  const will = which === "mapping" ? C.mapWill : C.rulWill;
  return (
    <>
      <PageHead title={title} />
      <div className={styles.soonPanel}>
        <p className={styles.soonTag}>{C.soonTag}</p>
        <p className={styles.soonWill}>{will}</p>
        <span className={styles.soonRule} aria-hidden />
        <p className={styles.soonNote}>{C.soonNothing}</p>
        <Link href="/dashboard" className={styles.soonLink}>
          {C.soonBack}
        </Link>
      </div>
    </>
  );
}
