"use client";

import { useEffect, useState } from "react";
import { ChatEntry } from "@/components/ChatEntry";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { AttachDocument, type Attachment } from "@/components/dashboard/AttachDocument";
import { PageHead } from "@/components/dashboard/DashParts";
import { detachActiveBestEffort } from "@/lib/documents";

export default function WorkspacePage() {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  /** Starting text handed over by Case history ("Open") or Mapping; read once, then cleared. */
  const [carry, setCarry] = useState<string | null>(null);
  /** The chat's conversation id: the attach and detach calls use the same one. */
  const [conversationId] = useState(() => `web-${crypto.randomUUID()}`);
  const [attachment, setAttachment] = useState<Attachment | null>(null);
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

  /** Leaving the Workspace drops the attachment from this chat (nothing is sent if none is attached). */
  useEffect(
    () => () => {
      void detachActiveBestEffort();
    },
    [],
  );

  return (
    <>
      <PageHead title={C.wsTitle} lede={C.wsLede} />
      <AttachDocument
        conversationId={conversationId}
        attachment={attachment}
        onAttach={setAttachment}
        onRemove={() => setAttachment(null)}
      />
      {carry === null ? null : (
        <ChatEntry
          hideCounter
          hideExamples
          unlimited
          initialDraft={carry}
          conversationId={conversationId}
          documentName={attachment?.name ?? null}
        />
      )}
    </>
  );
}
