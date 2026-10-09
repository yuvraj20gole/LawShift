"use client";

import { FormEvent, useCallback, useEffect, useId, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import type { Dictionary } from "@/lib/i18n";
import { usePrefs } from "@/lib/prefs";
import { authHeaders } from "@/lib/api";
import { useSession } from "@/lib/useSession";
import { labelToIso, saveCase } from "@/lib/caseHistory";
import {
  AnswerCard,
  CheckIcon,
  FlagIcon,
  displayConclusion,
  formatOffenseDateUsedLine,
  parseFixedConclusion,
  parseOffenseDateUsed,
  parseSources,
  parseVerification,
  stripIndexingContext,
  toSavedResult,
  type CardData,
  type Irac,
} from "./AnswerCard";
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

type BifurcationOption = { section: string; description: string };

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

type Msg =
  | { role: "user"; text: string }
  | ({
      role: "assistant";
      text: string;
      bifurcationOptions?: BifurcationOption[];
      sectionLookup?: SectionLookupItem[];
    } & CardData);

function sectionHasExceptionNotice(text: string): boolean {
  return /\b(Exception|Explanation|Proviso)\b/.test(text);
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

/** Saves a mapped answer (metadata plus the finished answer card) for a logged-in user. Non-blocking; failures are ignored. */
function saveMapped(
  data: Record<string, unknown>,
  question: string,
  language: string,
  documentName: string | null | undefined,
  card: CardData,
) {
  const badge = data.badge as { code?: string; section?: string; offenceName?: string } | undefined;
  if (!badge || typeof badge.code !== "string" || typeof badge.section !== "string") return;
  const odu = data.offense_date_used as { label?: string } | undefined;
  const v = data.verification as { flagged?: boolean } | undefined;
  const offenceDate = labelToIso(odu?.label);
  let result: unknown;
  try {
    result = toSavedResult(card, {
      code: badge.code,
      section: badge.section,
      heading: typeof badge.offenceName === "string" ? badge.offenceName : null,
      offence_date: offenceDate,
      date_source: (data.offense_date_used as { source?: string } | undefined)?.source ?? null,
    });
  } catch {
    result = undefined; // the row is still saved, without the answer
  }
  void saveCase({
    question: documentName ? `[Document: ${documentName}] ${question}`.slice(0, 4000) : question,
    offence_date: offenceDate,
    code: badge.code,
    section: badge.section,
    heading: typeof badge.offenceName === "string" ? badge.offenceName : null,
    flagged: Boolean(v?.flagged),
    language,
    result,
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
  const sendRef = useRef<(text: string, display?: string) => Promise<void>>(async () => {});

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

  /** A saved History answer can ask for its question to be run again. */
  useEffect(() => {
    function onRun(e: Event) {
      const text = (e as CustomEvent<{ text?: string }>).detail?.text;
      if (text) void sendRef.current(text);
    }
    window.addEventListener("lawshift:run", onRun);
    return () => window.removeEventListener("lawshift:run", onRun);
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
        const irac: Irac = { ...((data.irac as Irac) || {}) };
        if (typeof data.application_text === "string" && data.application_text) {
          irac.application = data.application_text;
        }
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
          irac.rule ? `${t.ruleStatute}: ${irac.rule}` : null,
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
          ruleTruncated: data.rule_truncated === true,
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
        const reply = replyFromData(data);
        setMessages((m) => [...m, reply]);
        // Free-question limit: only mapped answers count (not clarify /
        // bifurcation / failure). Network errors never reach here.
        if (data.kind === "mapping") {
          saveMapped(data, trimmed, lang, documentNameRef.current, reply as CardData);
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
        const reply = replyFromData(data);
        setMessages((m) => [...m, reply]);
        // Mapped answer after a bifurcation choice counts once.
        if (data.kind === "mapping") {
          saveMapped(data, heldQuestion.current, lang, documentNameRef.current, reply as CardData);
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

  sendRef.current = send;

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
                  <AnswerCard card={m} />
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
