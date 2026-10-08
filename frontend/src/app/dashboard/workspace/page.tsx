"use client";

import { useEffect, useState } from "react";
import { ChatEntry } from "@/components/ChatEntry";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { AttachDocument } from "@/components/dashboard/AttachDocument";
import { PageHead } from "@/components/dashboard/DashParts";

export default function WorkspacePage() {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  /** Starting text handed over by Case history ("Open") or Mapping; read once, then cleared. */
  const [carry, setCarry] = useState<string | null>(null);
  useEffect(() => {
    let text = "";
    try {
      text = sessionStorage.getItem("lawshift-carry") ?? "";
      sessionStorage.removeItem("lawshift-carry");
    } catch {
      /* start empty */
    }
    // Strict Mode runs this effect twice; the second read finds the key already cleared.
    setCarry((prev) => prev ?? text);
  }, []);

  return (
    <>
      <PageHead title={C.wsTitle} lede={C.wsLede} />
      <AttachDocument />
      {carry === null ? null : <ChatEntry hideCounter hideExamples unlimited initialDraft={carry} />}
    </>
  );
}
