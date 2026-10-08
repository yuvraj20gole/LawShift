"use client";

import { FormEvent, useCallback, useEffect, useId, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import type { Dictionary } from "@/lib/i18n";
import { usePrefs } from "@/lib/prefs";
import { authHeaders } from "@/lib/api";
import { useSession } from "@/lib/useSession";
import { labelToIso, saveCase } from "@/lib/caseHistory";
import styles from "./ChatEntry.module.css";

/** Hit FastAPI directly so long IRAC+translate jobs are not cut by the Next rewrite proxy. */
const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://127.0.0.1:8000";

/** The three cases the pipeline was smoke-tested on (PROCESS_LOG §18). */
const EXAMPLES = [
  {
    en: "On 5 September 2024, a person was found in possession of counterfeit currency notes.",
    hi: "5 सितंबर 2024 को एक व्यक्ति नकली मुद्रा नोटों के साथ पाया गया।",
    mr: "5 सप्टेंबर 2024 रोजी एका व्यक्तीकडे बनावट चलनी नोटा सापडल्या.",
  },
  {
    en: "On 10 August 2024, a riot occurred for a landowner's benefit and the agent failed to prevent it.",
    hi: "10 अगस्त 2024 को एक ज़मींदार के लाभ के लिए दंगा हुआ और एजेंट उसे रोकने में विफल रहा।",
    mr: "10 ऑगस्ट 2024 रोजी जमीनदाराच्या फायद्यासाठी दंगा झाला आणि एजंट तो रोखण्यात अयशस्वी ठरला.",
  },
  {
    en: "On 25 June 2024, a bookstore owner sold obscene magazines for the first time.",
    hi: "25 जून 2024 को एक पुस्तक विक्रेता ने पहली बार अश्लील पत्रिकाएँ बेचीं।",
    mr: "25 जून 2024 रोजी एका पुस्तक विक्रेत्याने पहिल्यांदा अश्लील मासिके विकली.",
  },
] as const;

type Irac = {
  issue?: string;
  rule?: string;
  application?: string;
  conclusion?: string;
};

type BifurcationOption = { section: string; description: string };

type Source = {
  statute?: string;
  section?: string;
  text?: string;
};

type Verification = {
  flagged?: boolean;
  confidence_note?: string;
};

type SectionLookupItem = {
  code: string;
  section: string;
  heading: string;
  text: string;
  found: boolean;
  mapping_line: string;
  mapping_status?: "equivalent" | "none" | "missing" | null;
  equiv_code?: string | null;
  equiv_section?: string | null;
  equiv_heading?: string | null;
  mapping_type?: "section" | "partial" | "merged" | null;
};

type OffenseDateUsed = {
  label: string;
  code: "IPC" | "BNS";
  source: "message" | "earlier_message" | "document" | "confirmed";
};

type FixedConclusionParts = {
  code: string;
  section: string;
  heading: string;
};

type Msg =
  | { role: "user"; text: string }
  | {
      role: "assistant";
      text: string;
      summary?: string;
      irac?: Irac;
      sources?: Source[];
      verification?: Verification | null;
      language?: string;
      engine?: "indictrans2" | "ollama_fallback" | "unavailable" | null;
      translationNote?: string | null;
      translationFallbackFields?: string[] | null;
      bifurcationOptions?: BifurcationOption[];
      sectionLookup?: SectionLookupItem[];
      offenseDateUsed?: OffenseDateUsed;
      fixedConclusion?: FixedConclusionParts;
      showExceptionNotice?: boolean;
      showScope?: boolean;
    };

function parseFixedConclusion(raw: unknown): FixedConclusionParts | undefined {
  if (!raw || typeof raw !== "object") return undefined;
  const o = raw as Record<string, unknown>;
  if (typeof o.code !== "string" || typeof o.section !== "string") return undefined;
  return {
    code: o.code,
    section: o.section,
    heading: typeof o.heading === "string" ? o.heading : "",
  };
}

function displayConclusion(
  irac: Irac,
  fixed: FixedConclusionParts | undefined,
  lang: string,
  dict: { fixedConclusion: (code: string, section: string, heading: string) => string },
): string | undefined {
  if (fixed) {
    return dict.fixedConclusion(fixed.code, fixed.section, fixed.heading || "");
  }
  return irac.conclusion;
}

/** Display-only: strip corpus indexing prefix from statute text. */
function stripIndexingContext(text: string): string {
  return text.replace(/^\[Context:[^\]]*\]\s*/i, "");
}

function sectionHasExceptionNotice(text: string): boolean {
  return /\b(Exception|Explanation|Proviso)\b/.test(text);
}

function parseOffenseDateUsed(raw: unknown): OffenseDateUsed | undefined {
  if (!raw || typeof raw !== "object") return undefined;
  const o = raw as Record<string, unknown>;
  if (typeof o.label !== "string") return undefined;
  if (o.code !== "IPC" && o.code !== "BNS") return undefined;
  const source =
    o.source === "earlier_message" || o.source === "document" || o.source === "confirmed"
      ? o.source
      : "message";
  return { label: o.label, code: o.code, source };
}

function formatOffenseDateUsedLine(
  odu: OffenseDateUsed,
  lang: string,
  dict: Dictionary,
): string {
  // EN example: "Indian Penal Code" (drop leading "the " from dictionary names).
  const rawName = odu.code === "IPC" ? dict.codeNameIpc : dict.codeNameBns;
  const codeName = rawName.replace(/^the\s+/i, "");
  const origin =
    odu.source === "earlier_message"
      ? dict.offenseDateFromEarlier
      : odu.source === "document"
        ? dict.offenseDateFromDocument
        : odu.source === "confirmed"
          ? dict.offenseDateConfirmed
          : "";
  const base = dict.offenseDateUsedLine(odu.label, codeName);
  return origin ? `${base} ${origin}` : base;
}

function langDisplayName(lang: string, dict: Dictionary): string {
  if (lang === "hi") return dict.langNameHi;
  if (lang === "mr") return dict.langNameMr;
  return dict.langNameEn;
}

/** English API sentinel for the bifurcation escape option. */
const DESCRIBE_FACTS_SENTINEL = "None of these. I will describe what happened";

function isDescribeFactsOption(section: string) {
  const s = section.trim().toLowerCase();
  return (
    s.startsWith("none of these") ||
    s.startsWith("इनमें से कोई नहीं") ||
    s.startsWith("यापैकी कोणतेही नाही")
  );
}

function statuteOptions(options: BifurcationOption[]) {
  return options.filter((o) => !isDescribeFactsOption(o.section));
}

function localizeMappingLine(
  item: SectionLookupItem,
  lang: string,
  dict: {
    sectionLookupNoEquivalent: string;
    sectionLookupMissing: (code: string, section: string) => string;
    sectionLookupMapping: (
      otherCodeName: string,
      phrase: string,
      label: string,
      heading: string,
    ) => string;
    mappingPhraseSection: string;
    mappingPhrasePartial: string;
    mappingPhraseMerged: string;
    codeNameIpc: string;
    codeNameBns: string;
  },
): string {
  if (lang === "en") return item.mapping_line;
  if (item.mapping_status === "missing" || (!item.found && item.mapping_line)) {
    return dict.sectionLookupMissing(item.code, item.section);
  }
  if (item.mapping_status === "none" || !item.equiv_section) {
    // Prefer structured "none"; also cover English-only "No equivalent…" lines.
    if (
      item.mapping_status === "none" ||
      item.mapping_line.startsWith("No equivalent")
    ) {
      return dict.sectionLookupNoEquivalent;
    }
  }
  if (item.mapping_status === "equivalent" && item.equiv_code && item.equiv_section) {
    const phrase =
      item.mapping_type === "partial"
        ? dict.mappingPhrasePartial
        : item.mapping_type === "merged"
          ? dict.mappingPhraseMerged
          : dict.mappingPhraseSection;
    const otherName =
      item.equiv_code === "IPC" ? dict.codeNameIpc : dict.codeNameBns;
    return dict.sectionLookupMapping(
      otherName,
      phrase,
      `${item.equiv_code} ${item.equiv_section}`,
      item.equiv_heading || "",
    );
  }
  return item.mapping_line;
}

function withDateLockNote(
  text: string,
  label: unknown,
  lang: string,
  dict: { dateLockNote: (date: string) => string },
  skipWhenOffenseDateUsed?: boolean,
): string {
  if (skipWhenOffenseDateUsed) return text;
  if (typeof label !== "string" || !label.trim()) return text;
  const note = dict.dateLockNote(label.trim());
  return text ? `${note}\n\n${text}` : note;
}

function withInfoNote(text: string, note: unknown): string {
  if (typeof note !== "string" || !note.trim()) return text;
  return text ? `${note.trim()}\n\n${text}` : note.trim();
}

function newConversationId() {
  return `web-${crypto.randomUUID()}`;
}

function parseSources(raw: unknown): Source[] {
  if (!Array.isArray(raw)) return [];
  return raw
    .filter((s): s is Record<string, unknown> => !!s && typeof s === "object")
    .map((s) => ({
      statute: typeof s.statute === "string" ? s.statute : undefined,
      section: typeof s.section === "string" ? s.section : undefined,
      text: typeof s.text === "string" ? s.text : undefined,
    }));
}

function parseVerification(raw: unknown): Verification | null {
  if (!raw || typeof raw !== "object") return null;
  const v = raw as Record<string, unknown>;
  return {
    flagged: Boolean(v.flagged),
    confidence_note:
      typeof v.confidence_note === "string" ? v.confidence_note : undefined,
  };
}

function CheckIcon() {
  return (
    <svg viewBox="0 0 16 16" width="16" height="16" fill="none" aria-hidden>
      <path
        d="M3.5 8.5l3 3 6-7"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function FlagIcon() {
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

/** Saves a mapped answer's metadata for a logged-in user. Non-blocking; failures are ignored. */
function saveMapped(data: Record<string, unknown>, question: string, language: string, documentName?: string | null) {
  const badge = data.badge as { code?: string; section?: string; offenceName?: string } | undefined;
  if (!badge || typeof badge.code !== "string" || typeof badge.section !== "string") return;
  const odu = data.offense_date_used as { label?: string } | undefined;
  const v = data.verification as { flagged?: boolean } | undefined;
  void saveCase({
    question: documentName ? `[Document: ${documentName}] ${question}`.slice(0, 4000) : question,
    offence_date: labelToIso(odu?.label),
    code: badge.code,
    section: badge.section,
    heading: typeof badge.offenceName === "string" ? badge.offenceName : null,
    flagged: Boolean(v?.flagged),
    language,
  });
}

type ChatEntryProps = {
  /** Hide the "N questions left" line (signed-in views). */
  hideCounter?: boolean;
  /** Hide the example-prompt buttons in the empty state. */
  hideExamples?: boolean;
  /** Signed-in users have no quota: never block on the visitor limit. */
  unlimited?: boolean;
  /** Text to start the composer with (carried over from another screen). */
  initialDraft?: string;
  /** Use this conversation id (the Workspace needs it to attach a document to the same chat). */
  conversationId?: string;
  /** Name of the attached document: the saved History question is prefixed with it. */
  documentName?: string | null;
};

export function ChatEntry({
  hideCounter = false,
  hideExamples = false,
  unlimited = false,
  initialDraft = "",
  conversationId: conversationIdProp,
  documentName = null,
}: ChatEntryProps = {}) {
  const { lang, t } = usePrefs();
  const reduceMotion = useReducedMotion();
  const inputId = useId();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [draft, setDraft] = useState(initialDraft);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [busy, setBusy] = useState(false);
  const [remaining, setRemaining] = useState(5);
  const { email: sessionEmail } = useSession();
  const outOfQuota = !unlimited && !sessionEmail && remaining <= 0;
  const [ownConversationId] = useState(newConversationId);
  const conversationId = conversationIdProp ?? ownConversationId;
  const documentNameRef = useRef<string | null>(documentName);
  documentNameRef.current = documentName;
  /** The user's own message that started the current case (kept across bifurcation choices). */
  const heldQuestion = useRef("");
  const [error, setError] = useState<string | null>(null);
  const [landed, setLanded] = useState(0);
  /** Expanded source bodies: `${messageIndex}:${sourceIndex}` */
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>(
    {},
  );
  const [langSwitchNote, setLangSwitchNote] = useState<string | null>(null);
  const prevLangRef = useRef(lang);

  /** The landing page's recorded cases hand their text to the composer. */
  useEffect(() => {
    function onAsk(e: Event) {
      const text = (e as CustomEvent<{ text?: string }>).detail?.text;
      if (!text) return;
      setDraft(text);
      setLanded((n) => n + 1);
      textareaRef.current?.focus({ preventScroll: true });
    }
    window.addEventListener("lawshift:ask", onAsk);
    return () => window.removeEventListener("lawshift:ask", onAsk);
  }, []);

  useEffect(() => {
    if (prevLangRef.current === lang) return;
    const hadAssistant = messages.some((m) => m.role === "assistant");
    if (hadAssistant) {
      setLangSwitchNote(t.langSwitchNote(langDisplayName(lang, t)));
    }
    prevLangRef.current = lang;
  }, [lang, messages, t]);

  const replyFromData = useCallback(
    (data: Record<string, unknown>): Msg => {
      if (data.kind === "mapping") {
        const irac: Irac = (data.irac as Irac) || {};
        const sources = parseSources(data.sources);
        const offenseDateUsed = parseOffenseDateUsed(data.offense_date_used);
        const fixedConclusion = parseFixedConclusion(data.fixed_conclusion);
        const conclusionText = displayConclusion(irac, fixedConclusion, lang, t);
        const rawVerification = parseVerification(data.verification);
        /* The all-clear line is fixed copy, so show it in the reader's language. */
        const verification = rawVerification
          ? { ...rawVerification, confidence_note: rawVerification.flagged ? rawVerification.confidence_note : t.verifyOk }
          : null;
        const parts = [
          data.summary ? `${t.mapped}: ${data.summary}` : null,
          irac.issue ? `${t.issue}: ${irac.issue}` : null,
          irac.rule ? `${t.rule}: ${irac.rule}` : null,
          irac.application ? `${t.application}: ${irac.application}` : null,
          conclusionText ? `${t.conclusion}: ${conclusionText}` : null,
          verification?.flagged
            ? `${t.verifierNote}: ${verification.confidence_note || t.worthDoubleChecking}`
            : verification
              ? `${t.verifierNote}: ${t.verifyOk}`
              : null,
        ].filter(Boolean);
        let text = withDateLockNote(
          parts.join("\n\n"),
          data.date_lock_label,
          lang,
          t,
          Boolean(offenseDateUsed),
        );
        const showExceptionNotice = sources.some(
          (s) => s.text && sectionHasExceptionNotice(s.text),
        );
        // Prefer localised missing-section search note when the API sent English.
        let infoNote =
          typeof data.info_note === "string" ? data.info_note : null;
        if (infoNote && lang !== "en") {
          const m = infoNote.match(
            /^([A-Z]+)\s+(\S+)\s+is not in the statute text we hold/i,
          );
          if (m) infoNote = t.sectionMissingSearchNote(m[1], m[2]);
        }
        text = withInfoNote(text, infoNote);
        return {
          role: "assistant",
          text,
          summary: data.summary as string | undefined,
          irac: conclusionText ? { ...irac, conclusion: conclusionText } : irac,
          sources,
          verification,
          offenseDateUsed,
          fixedConclusion,
          showExceptionNotice,
          showScope: true,
          language: lang,
          engine:
            data.engine === "indictrans2" ||
            data.engine === "ollama_fallback" ||
            data.engine === "unavailable"
              ? data.engine
              : null,
          translationNote:
            typeof data.translation_note === "string" ? data.translation_note : null,
          translationFallbackFields: Array.isArray(data.translation_fallback_fields)
            ? (data.translation_fallback_fields as unknown[]).filter(
                (x): x is string => typeof x === "string",
              )
            : null,
        };
      }
      if (data.kind === "clarify") {
        const factsClarify = data.reason === "missing_facts";
        const mismatchClarify = data.reason === "code_mismatch";
        const describeClarify = data.reason === "describe_facts";
        const fallback = mismatchClarify
          ? t.clarifyFallbackMismatch
          : describeClarify
            ? t.clarifyFallbackDescribeFacts
            : factsClarify
              ? t.clarifyFallbackFacts
              : t.clarifyFallback;
        let text =
          lang === "en" ? (data.question as string) || fallback : fallback;
        text = withDateLockNote(text, data.date_lock_label, lang, t);
        return {
          role: "assistant",
          text,
          language: lang,
        };
      }
      if (data.kind === "section_lookup") {
        const offenseDateUsed = parseOffenseDateUsed(data.offense_date_used);
        const rawItems = Array.isArray(data.items) ? data.items : [];
        const items: SectionLookupItem[] = rawItems
          .filter((it): it is Record<string, unknown> => !!it && typeof it === "object")
          .map((it) => {
            const base: SectionLookupItem = {
              code: typeof it.code === "string" ? it.code : "",
              section: typeof it.section === "string" ? it.section : "",
              heading: typeof it.heading === "string" ? it.heading : "",
              text: typeof it.text === "string" ? it.text : "",
              found: Boolean(it.found),
              mapping_line:
                typeof it.mapping_line === "string" ? it.mapping_line : "",
              mapping_status:
                it.mapping_status === "equivalent" ||
                it.mapping_status === "none" ||
                it.mapping_status === "missing"
                  ? it.mapping_status
                  : null,
              equiv_code: typeof it.equiv_code === "string" ? it.equiv_code : null,
              equiv_section:
                typeof it.equiv_section === "string" ? it.equiv_section : null,
              equiv_heading:
                typeof it.equiv_heading === "string" ? it.equiv_heading : null,
              mapping_type:
                it.mapping_type === "section" ||
                it.mapping_type === "partial" ||
                it.mapping_type === "merged"
                  ? it.mapping_type
                  : null,
            };
            return {
              ...base,
              mapping_line: localizeMappingLine(base, lang, t),
            };
          });
        let text =
          data.reason === "bifurcation_exhausted"
            ? lang === "en"
              ? (data.note as string) || t.sectionLookupExhaustedNote
              : t.sectionLookupExhaustedNote
            : lang === "en"
              ? (data.note as string) || t.sectionLookupNoteFallback
              : t.sectionLookupNoteFallback;
        text = withDateLockNote(
          text,
          data.date_lock_label,
          lang,
          t,
          Boolean(offenseDateUsed),
        );
        return {
          role: "assistant",
          text,
          language: lang,
          sectionLookup: items,
          offenseDateUsed,
        };
      }
      if (data.kind === "bifurcation") {
        const options = (data.options as BifurcationOption[]) || [];
        const mismatch = data.reason === "code_mismatch";
        const dateConflict = data.reason === "date_conflict";
        const statuteSecs = statuteOptions(options)
          .map((o) => o.section)
          .join(", ");
        const shortIpc = t.codeNameIpc.replace(/^the\s+/i, "");
        const shortBns = t.codeNameBns.replace(/^the\s+/i, "");
        // Localise the escape option label; keep English sentinel for resolve.
        // Date-conflict options keep date labels; localise code descriptions.
        const localized = options.map((o) => {
          if (isDescribeFactsOption(o.section)) {
            return {
              section: DESCRIBE_FACTS_SENTINEL,
              description: t.bifurcationEscapeOption,
            };
          }
          if (dateConflict && lang !== "en") {
            const isIpc = /penal|दंड|दंड/i.test(o.description);
            return {
              section: o.section,
              description: isIpc ? shortIpc : shortBns,
            };
          }
          return o;
        });
        let text: string;
        if (lang === "en") {
          text = (data.prompt as string) || "";
        } else if (dateConflict && options.length >= 2) {
          text = t.bifurcationDateConflictFallback(
            options[0].section,
            /penal/i.test(options[0].description) ? shortIpc : shortBns,
            options[1].section,
            /penal/i.test(options[1].description) ? shortIpc : shortBns,
          );
        } else if (mismatch) {
          text = t.bifurcationMismatchFallback(statuteSecs);
        } else {
          text = t.bifurcationPrompt(statuteSecs);
        }
        text = withDateLockNote(text, data.date_lock_label, lang, t);
        let infoNote =
          typeof data.info_note === "string" ? data.info_note : null;
        if (infoNote && lang !== "en") {
          const m = infoNote.match(
            /^([A-Z]+)\s+(\S+)\s+is not in the statute text we hold/i,
          );
          if (m) infoNote = t.sectionMissingSearchNote(m[1], m[2]);
        }
        text = withInfoNote(text, infoNote);
        return {
          role: "assistant",
          text,
          language: lang,
          bifurcationOptions: localized,
        };
      }
      if (data.kind === "failure") {
        return {
          role: "assistant",
          text: withDateLockNote(
            (data.message as string) || t.failureFallback,
            data.date_lock_label,
            lang,
            t,
          ),
          language: lang,
        };
      }
      return { role: "assistant", text: t.unexpected, language: lang };
    },
    [lang, t],
  );

  const send = useCallback(
    async (text: string, display?: string) => {
      const trimmed = text.trim();
      if (!trimmed || busy || outOfQuota) return;

      setError(null);
      setBusy(true);
      setDraft("");
      heldQuestion.current = trimmed;
      setMessages((m) => [...m, { role: "user", text: display ?? trimmed }]);

      try {
        const res = await fetch(`${API_BASE}/api/query`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...(await authHeaders()) },
          body: JSON.stringify({
            message: trimmed,
            conversation_id: conversationId,
            language: lang,
          }),
        });
        const data = await res.json();
        setMessages((m) => [...m, replyFromData(data)]);
        // Free-question limit: only mapped answers count (not clarify /
        // bifurcation / failure). Network errors never reach here.
        if (data.kind === "mapping") {
          saveMapped(data, trimmed, lang, documentNameRef.current);
          setRemaining((n) => Math.max(0, n - 1));
        }
      } catch {
        setError(t.apiError);
        setMessages((m) => m.slice(0, -1));
        setDraft(trimmed);
      } finally {
        setBusy(false);
      }
    },
    [busy, conversationId, lang, outOfQuota, replyFromData, t],
  );

  const resolveBifurcation = useCallback(
    async (section: string, display?: string) => {
      if (!section || busy) return;
      const escape = isDescribeFactsOption(section);
      if (outOfQuota && !escape) return;
      setError(null);
      setBusy(true);
      setMessages((m) => [
        ...m,
        { role: "user", text: display ?? section },
      ]);
      try {
        const res = await fetch(`${API_BASE}/api/query/resolve_bifurcation`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...(await authHeaders()) },
          body: JSON.stringify({
            conversation_id: conversationId,
            chosen_section: section,
            language: lang,
          }),
        });
        const data = await res.json();
        setMessages((m) => [...m, replyFromData(data)]);
        // Mapped answer after a bifurcation choice counts once.
        if (data.kind === "mapping") {
          saveMapped(data, heldQuestion.current, lang, documentNameRef.current);
          setRemaining((n) => Math.max(0, n - 1));
        }
      } catch {
        setError(t.apiError);
        setMessages((m) => m.slice(0, -1));
      } finally {
        setBusy(false);
      }
    },
    [busy, conversationId, lang, outOfQuota, replyFromData, t],
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void send(draft);
  }

  function toggleSource(messageIndex: number, sourceIndex: number) {
    const key = `${messageIndex}:${sourceIndex}`;
    setExpandedSources((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  return (
    <div className={styles.shell}>
      {langSwitchNote ? (
        <p className={styles.langSwitchNote} role="status">
          {langSwitchNote}
        </p>
      ) : null}
      <div className={styles.thread} aria-live="polite" tabIndex={0} data-lenis-prevent>
        {messages.length === 0 ? (
          <div className={styles.empty}>
            <p className={styles.emptyTitle}>{t.emptyTitle}</p>
            <p className={styles.emptyBody}>{t.emptyBody}</p>
            {hideExamples ? null : (
              <div className={styles.examples}>
                {EXAMPLES.map((ex) => (
                  <button
                    key={ex.en}
                    type="button"
                    className={styles.example}
                    onClick={() => void send(ex.en, ex[lang])}
                    disabled={busy || outOfQuota}
                    lang={lang}
                  >
                    {ex[lang]}
                  </button>
                ))}
              </div>
            )}
            <div className={styles.verifyLegend} aria-label="Verification note examples">
              <p className={styles.verifyOk}>
                <span className={styles.verifyMark}>
                  <CheckIcon />
                </span>
                <span>{t.verifyOk}</span>
              </p>
              <p className={styles.verifyFlagged}>
                <span className={styles.verifyMark}>
                  <FlagIcon />
                </span>
                <span>
                  <strong>{t.worthDoubleChecking}</strong>
                  <span className={styles.verifyNote}>
                    Shown when the conclusion may not follow from the statute text.
                  </span>
                </span>
              </p>
            </div>
          </div>
        ) : (
          <ul className={styles.messages}>
            {messages.map((m, i) => (
              <li
                key={`${m.role}-${i}`}
                className={m.role === "user" ? styles.user : styles.assistant}
              >
                <span className={styles.role}>
                  {m.role === "user" ? t.you : t.assistant}
                </span>
                {m.role === "assistant" && m.irac ? (
                  <div className={styles.iracBlock}>
                    {m.offenseDateUsed ? (
                      <p className={styles.displayMeta}>
                        {formatOffenseDateUsedLine(m.offenseDateUsed, lang, t)}
                      </p>
                    ) : null}
                    {m.summary ? (
                      <p className={styles.summaryLine}>
                        {t.mapped}: {m.summary}
                      </p>
                    ) : null}
                    {(
                      [
                        ["issue", t.issue, m.irac.issue],
                        ["rule", t.rule, m.irac.rule],
                        ["application", t.application, m.irac.application],
                        [
                          "conclusion",
                          t.conclusion,
                          // Prefer the localised template from structured parts
                          // so HI/MR (and language switches) do not show the
                          // English fixed sentence baked at reply time.
                          displayConclusion(m.irac, m.fixedConclusion, lang, t) ??
                            m.irac.conclusion,
                        ],
                      ] as const
                    ).map(([key, label, value]) =>
                      value ? (
                        <div key={key} className={styles.iracField}>
                          <span className={styles.iracLabel}>{label}</span>
                          {/* One grid cell for note + body — a third child would
                              wrap into the 6.25rem label column and squeeze text. */}
                          <div className={styles.iracValue}>
                            {key === "application" ? (
                              <p className={styles.generatedNote}>
                                {t.generatedNote}
                              </p>
                            ) : null}
                            <p className={styles.statute}>{value}</p>
                          </div>
                        </div>
                      ) : null,
                    )}

                    {m.sources && m.sources.length > 0 ? (
                      <div className={styles.sourcesBlock}>
                        <span className={styles.iracLabel}>
                          {t.sourcesHeading(m.sources.length)}
                        </span>
                        <ul className={styles.sourcesList}>
                          {m.sources.map((src, si) => {
                            const key = `${i}:${si}`;
                            const open = Boolean(expandedSources[key]);
                            const cite = [src.statute, src.section]
                              .filter(Boolean)
                              .join(" ");
                            return (
                              <li key={key} className={styles.sourceItem}>
                                <button
                                  type="button"
                                  className={styles.sourceToggle}
                                  aria-expanded={open}
                                  onClick={() => toggleSource(i, si)}
                                >
                                  <strong>{cite || t.sourcesHeading(1)}</strong>
                                  <span>
                                    {open ? t.hideSourceText : t.showSourceText}
                                  </span>
                                </button>
                                <AnimatePresence initial={false}>
                                  {open && src.text ? (
                                    <motion.div
                                      key="src"
                                      className={styles.sourceTextWrap}
                                      initial={
                                        reduceMotion
                                          ? { opacity: 0 }
                                          : { height: 0, opacity: 0 }
                                      }
                                      animate={
                                        reduceMotion
                                          ? { opacity: 1 }
                                          : { height: "auto", opacity: 1 }
                                      }
                                      exit={
                                        reduceMotion
                                          ? { opacity: 0 }
                                          : { height: 0, opacity: 0 }
                                      }
                                      transition={
                                        reduceMotion
                                          ? { duration: 0.12 }
                                          : {
                                              height: {
                                                duration: 0.2,
                                                ease: [0.23, 1, 0.32, 1],
                                              },
                                              opacity: { duration: 0.15 },
                                            }
                                      }
                                    >
                                      <p className={styles.sourceText}>
                                        {stripIndexingContext(src.text ?? "")}
                                      </p>
                                    </motion.div>
                                  ) : null}
                                </AnimatePresence>
                              </li>
                            );
                          })}
                        </ul>
                      </div>
                    ) : null}

                    {m.verification ? (
                      <div
                        className={
                          m.verification.flagged ? styles.verifyFlagged : styles.verifyOk
                        }
                        role="status"
                      >
                        {m.verification.flagged ? (
                          <>
                            <span className={styles.verifyMark}>
                              <FlagIcon />
                            </span>
                            <div>
                              <strong>{t.worthDoubleChecking}</strong>
                              {m.verification.confidence_note ? (
                                <p className={styles.verifyNote}>
                                  {m.verification.confidence_note}
                                </p>
                              ) : null}
                            </div>
                          </>
                        ) : (
                          <>
                            <span className={styles.verifyMark}>
                              <CheckIcon />
                            </span>
                            <span>{m.verification.confidence_note || t.verifyOk}</span>
                          </>
                        )}
                      </div>
                    ) : null}

                    {m.showScope ? (
                      <p className={styles.displayMeta}>{t.scopeLine}</p>
                    ) : null}
                    {m.showExceptionNotice ? (
                      <p className={styles.displayMeta}>{t.exceptionProvisoNotice}</p>
                    ) : null}

                    {m.language && m.language !== "en" && m.engine === "indictrans2" ? (
                      <p className={styles.fallbackNote}>{t.machineTranslatedNote}</p>
                    ) : null}
                    {m.translationFallbackFields &&
                    m.translationFallbackFields.length > 0 ? (
                      <p className={styles.fallbackNote}>
                        {t.numberGuardFallbackNote}
                      </p>
                    ) : null}
                    {m.engine === "ollama_fallback" ? (
                      <p className={styles.fallbackNote}>
                        {m.translationNote || t.translationFallbackNote}
                      </p>
                    ) : null}
                    {m.engine === "unavailable" && m.translationNote ? (
                      <p className={styles.fallbackNote}>{m.translationNote}</p>
                    ) : null}
                  </div>
                ) : m.role === "assistant" && m.sectionLookup?.length ? (
                  <div className={styles.iracBlock}>
                    {m.offenseDateUsed ? (
                      <p className={styles.displayMeta}>
                        {formatOffenseDateUsedLine(m.offenseDateUsed, lang, t)}
                      </p>
                    ) : null}
                    <p className={styles.statute}>{m.text}</p>
                    {m.sectionLookup.map((item, si) => {
                      const key = `${i}:${si}`;
                      const open = Boolean(expandedSources[key]);
                      const cite = [item.code, item.section]
                        .filter(Boolean)
                        .join(" ");
                      const title =
                        item.found && item.heading
                          ? `${cite} — ${item.heading}`
                          : cite;
                      return (
                        <div key={`sl-${key}`}>
                          {item.mapping_line ? (
                            <p className={styles.statute}>{item.mapping_line}</p>
                          ) : null}
                          {!item.found ? (
                            <p className={styles.statute}>
                              <strong>{title || cite}</strong>
                            </p>
                          ) : null}
                          {item.found && item.text ? (
                            <div className={styles.sourcesBlock}>
                              <span className={styles.iracLabel}>
                                {t.sourcesHeading(1)}
                              </span>
                              <ul className={styles.sourcesList}>
                                <li className={styles.sourceItem}>
                                  <button
                                    type="button"
                                    className={styles.sourceToggle}
                                    aria-expanded={open}
                                    onClick={() => toggleSource(i, si)}
                                  >
                                    <strong>{title || cite}</strong>
                                    <span>
                                      {open
                                        ? t.hideSourceText
                                        : t.showSourceText}
                                    </span>
                                  </button>
                                  <AnimatePresence initial={false}>
                                    {open ? (
                                      <motion.div
                                        key="src"
                                        className={styles.sourceTextWrap}
                                        initial={
                                          reduceMotion
                                            ? { opacity: 0 }
                                            : { height: 0, opacity: 0 }
                                        }
                                        animate={
                                          reduceMotion
                                            ? { opacity: 1 }
                                            : { height: "auto", opacity: 1 }
                                        }
                                        exit={
                                          reduceMotion
                                            ? { opacity: 0 }
                                            : { height: 0, opacity: 0 }
                                        }
                                        transition={
                                          reduceMotion
                                            ? { duration: 0.12 }
                                            : {
                                                height: {
                                                  duration: 0.2,
                                                  ease: [0.23, 1, 0.32, 1],
                                                },
                                                opacity: { duration: 0.15 },
                                              }
                                        }
                                      >
                                        <p className={styles.sourceText}>
                                          {stripIndexingContext(item.text)}
                                        </p>
                                      </motion.div>
                                    ) : null}
                                  </AnimatePresence>
                                </li>
                              </ul>
                            </div>
                          ) : null}
                        </div>
                      );
                    })}
                  </div>
                ) : m.role === "assistant" && m.bifurcationOptions?.length ? (
                  <div className={styles.bifurcation}>
                    <p className={styles.statute}>{m.text}</p>
                    <div className={styles.bifurcationOptions}>
                      {m.bifurcationOptions.map((o) => {
                        const escape = isDescribeFactsOption(o.section);
                        const escapeLabel =
                          o.description || t.bifurcationEscapeOption;
                        return (
                          <button
                            key={o.section}
                            type="button"
                            className={styles.bifurcationBtn}
                            disabled={busy || (outOfQuota && !escape)}
                            onClick={() =>
                              void resolveBifurcation(
                                escape ? DESCRIBE_FACTS_SENTINEL : o.section,
                                escape ? escapeLabel : o.section,
                              )
                            }
                          >
                            {escape ? (
                              <strong>{escapeLabel}</strong>
                            ) : (
                              <>
                                <strong>{o.section}</strong>
                                {o.description ? (
                                  <span>{o.description}</span>
                                ) : null}
                              </>
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ) : (
                  <p className={m.role === "assistant" ? styles.statute : undefined}>
                    {m.text}
                  </p>
                )}
              </li>
            ))}
            {busy ? (
              <li className={styles.assistant} aria-live="polite">
                <span className={styles.role}>{t.assistant}</span>
                <p className={styles.working}>{t.running}</p>
              </li>
            ) : null}
          </ul>
        )}
      </div>

      <form className={styles.composer} onSubmit={onSubmit}>
        <label htmlFor={inputId} className="sr-only">
          {t.caseQuestion}
        </label>
        <textarea
          id={inputId}
          ref={textareaRef}
          key={landed}
          className={landed ? styles.landed : undefined}
          rows={2}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder={t.composerPlaceholder}
          disabled={busy || outOfQuota}
        />
        <button type="submit" disabled={busy || outOfQuota || !draft.trim()}>
          {busy ? t.running : t.send}
        </button>
      </form>

      {hideCounter || sessionEmail ? null : (
        <p className={styles.note}>{remaining === 1 ? t.freeOne : t.freeMany(remaining)}</p>
      )}
      {error ? (
        <p className={styles.error} role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
