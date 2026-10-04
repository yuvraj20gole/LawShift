"use client";

import { useState } from "react";
import Link from "next/link";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { SAMPLE_DOCS, type SampleDoc } from "@/lib/sampleData";
import { usePreviewMode } from "@/components/dashboard/DashboardShell";
import { Dropzone } from "@/components/dashboard/Dropzone";
import { EmptyState, PageHead } from "@/components/dashboard/DashParts";
import styles from "@/components/dashboard/dashboard.module.css";

export default function DocumentsPage() {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  const mode = usePreviewMode();
  const [docs, setDocs] = useState<SampleDoc[]>(mode === "empty" ? [] : SAMPLE_DOCS);

  const readLabel = (r: SampleDoc["read"]) =>
    r === "direct" ? C.readDirect : r === "ocr" ? C.readOcr : C.readPending;

  function add(files: File[]) {
    setDocs((d) => [
      ...files.map((f, i) => ({
        id: `new-${Date.now()}-${i}`,
        name: f.name,
        date: "3 Oct 2026",
        read: "pending" as const,
        foundDate: null,
      })),
      ...d,
    ]);
  }

  return (
    <>
      <PageHead title={C.dcTitle} lede={C.dcLede} />
      <Dropzone onFiles={add} />

      <h2 className={styles.listHead}>{C.dcListTitle}</h2>
      {docs.length === 0 ? (
        <EmptyState title={C.dcEmptyTitle} body={C.dcEmptyBody} />
      ) : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th scope="col">{C.colFile}</th>
                <th scope="col">{C.colDate}</th>
                <th scope="col">{C.colRead}</th>
                <th scope="col">{C.colResult}</th>
              </tr>
            </thead>
            <tbody>
              {docs.map((d, i) => (
                <tr key={d.id} style={{ ["--i" as string]: i }}>
                  <td data-label={C.colFile}>
                    <strong className={styles.fileName}>{d.name}</strong>
                  </td>
                  <td data-label={C.colDate}>{d.date}</td>
                  <td data-label={C.colRead}>
                    <span className={d.read === "ocr" ? styles.readOcr : styles.readPlain}>{readLabel(d.read)}</span>
                  </td>
                  <td data-label={C.colResult}>
                    {d.read === "pending" ? (
                      "—"
                    ) : (
                      <Link href="/dashboard/workspace" className={styles.linkBtn}>
                        {C.viewResult}
                        <span className="sr-only"> {d.name}</span>
                      </Link>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
