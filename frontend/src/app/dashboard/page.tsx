"use client";

import Link from "next/link";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { SAMPLE_CASES, SAMPLE_EMAIL, QUESTIONS_TOTAL, SAMPLE_QUESTIONS_LEFT } from "@/lib/sampleData";
import { usePreviewMode } from "@/components/dashboard/DashboardShell";
import { CodeBadge, EmptyState, PageHead, Row, Squares, VerifyState } from "@/components/dashboard/DashParts";
import styles from "@/components/dashboard/dashboard.module.css";

export default function OverviewPage() {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  const mode = usePreviewMode();
  const cases = mode === "empty" ? [] : SAMPLE_CASES.slice(0, 5);
  const left = mode === "empty" ? QUESTIONS_TOTAL : SAMPLE_QUESTIONS_LEFT;
  const leftText = C.ovQuestionsLeft(left, QUESTIONS_TOTAL);

  return (
    <>
      <PageHead title={C.ovTitle} lede={`${C.ovWelcome} ${SAMPLE_EMAIL}`} />

      <Row title={C.ovQuestionsTitle}>
        <div className={styles.counter}>
          <Squares filled={left} total={QUESTIONS_TOTAL} label={leftText} />
          <p className={styles.counterText}>{leftText}</p>
        </div>
        <p className={styles.note}>{C.ovQuestionsNote}</p>
        <Link href="/dashboard/workspace" className={styles.primary}>
          {C.describeCase}
        </Link>
      </Row>

      <Row title={C.ovRecentTitle}>
        {cases.length === 0 ? (
          <EmptyState
            title={C.ovEmptyTitle}
            body={C.ovEmptyBody}
            action={{ label: C.describeCase, href: "/dashboard/workspace" }}
          />
        ) : (
          <>
            <p className={styles.note}>{C.ovRecentLede}</p>
            <ul className={styles.recent}>
              {cases.map((c) => (
                <li key={c.id} className={styles.recentItem}>
                  <span className={styles.recentDate}>{c.asked}</span>
                  <span className={styles.recentSec}>
                    <CodeBadge code={c.code} />
                    <strong>{c.section}</strong>
                  </span>
                  <span className={styles.recentTitle}>{c.title}</span>
                  <VerifyState flagged={c.flagged} okText={C.verOk} flagText={C.verFlag} />
                  <Link href="/dashboard/workspace" className={styles.linkBtn}>
                    {C.open}
                  </Link>
                </li>
              ))}
            </ul>
            <Link href="/dashboard/history" className={styles.textLink}>
              {C.ovAllCases}
            </Link>
          </>
        )}
      </Row>
    </>
  );
}
