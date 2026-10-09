"use client";

import { useEffect, useRef, useState } from "react";
import { ChatEntry } from "@/components/ChatEntry";
import { usePrefs } from "@/lib/prefs";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import { AttachDocument, type Attachment } from "@/components/dashboard/AttachDocument";
import { PageHead } from "@/components/dashboard/DashParts";
import { detachActiveBestEffort } from "@/lib/documents";
import { loadSavedAnswer } from "@/lib/caseHistory";
import { parseSavedResult, type CardData } from "@/components/AnswerCard";
import { SavedAnswer } from "@/components/dashboard/SavedAnswer";
import d from "@/components/dashboard/dashboard.module.css";

export default function WorkspacePage() {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  /** Starting text handed over by Case history ("Open") or Mapping; read once, then cleared. */
  const [carry, setCarry] = useState<string | null>(null);
  /** The chat's conversation id: the attach and detach calls use the same one. */
  const [conversationId] = useState(() => `web-${crypto.randomUUID()}`);
  const [attachment, setAttachment] = useState<Attachment | null>(null);
  /** A saved History answer opened with "Open", shown read only above the chat. */
  const [saved, setSaved] = useState<{ question: string; card: CardData; createdAt: string } | null>(null);
  const [loadingSaved, setLoadingSaved] = useState(false);
  const [noSaved, setNoSaved] = useState(false);
  /** The question (with its date) the saved answer was asked with; used by the two buttons. */
  const [openingQuestion, setOpeningQuestion] = useState("");
  const started = useRef(false);
  useEffect(() => {
    // Strict Mode runs this effect twice; the ref makes the one-time read happen once.
    if (started.current) return;
    started.current = true;
    let text = "";
    let openId = "";
    try {
      text = sessionStorage.getItem("lawshift-carry") ?? "";
      openId = sessionStorage.getItem("lawshift-open") ?? "";
      sessionStorage.removeItem("lawshift-carry");
      sessionStorage.removeItem("lawshift-open");
    } catch {
      /* start empty */
    }
    if (!openId) {
      setCarry(text);
      return;
    }
    setLoadingSaved(true);
    void loadSavedAnswer(openId).then((row) => {
      const card = row ? parseSavedResult(row.result) : null;
      if (row && card) {
        setSaved({ question: row.question, card, createdAt: row.created_at });
        setOpeningQuestion(text || row.question);
        setCarry("");
      } else {
        setNoSaved(true);
        setCarry(text);
      }
      setLoadingSaved(false);
    });
  }, []);

  function followUp() {
    window.dispatchEvent(new CustomEvent("lawshift:ask", { detail: { text: openingQuestion } }));
  }
  function runAgain() {
    window.dispatchEvent(new CustomEvent("lawshift:run", { detail: { text: openingQuestion } }));
  }

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
      {loadingSaved ? (
        <p className={d.note} role="status">
          {C.savedLoading}
        </p>
      ) : null}
      {saved ? (
        <SavedAnswer
          question={saved.question}
          card={saved.card}
          createdAt={saved.createdAt}
          onFollowUp={followUp}
          onRunAgain={runAgain}
        />
      ) : null}
      {noSaved ? <p className={d.note}>{C.savedNone}</p> : null}
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
