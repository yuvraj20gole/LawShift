"use client";

import { useState } from "react";
import { ChatEntry } from "@/components/ChatEntry";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { Dropzone } from "@/components/dashboard/Dropzone";
import { PageHead } from "@/components/dashboard/DashParts";
import styles from "@/components/dashboard/dashboard.module.css";

export default function WorkspacePage() {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  const [names, setNames] = useState<string[]>([]);

  return (
    <>
      <PageHead title={C.wsTitle} lede={C.wsLede} />
      <ChatEntry />

      {/* Slot for the upload control: the same Dropzone the Documents page uses. */}
      <section className={styles.uploadSlot} aria-labelledby="ws-upload">
        <h2 id="ws-upload" className={styles.slotHead}>
          {C.wsUploadTitle}
        </h2>
        <Dropzone compact id="ws-dropzone" onFiles={(f) => setNames((n) => [...n, ...f.map((x) => x.name)])} />
        <p className={styles.note}>{C.wsUploadNote}</p>
        {names.length ? (
          <ul className={styles.picked}>
            {names.map((n, i) => (
              <li key={`${n}-${i}`}>{n}</li>
            ))}
          </ul>
        ) : null}
      </section>
    </>
  );
}
