"use client";

import { FormEvent, useCallback, useEffect, useId, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { usePrefs } from "@/lib/prefs";
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
      bifurcationOptions?: BifurcationOption[];
    };

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

export function ChatEntry() {
  const { lang, t } = usePrefs();
  const reduceMotion = useReducedMotion();
  const inputId = useId();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<Msg[]>([]);
  const [busy, setBusy] = useState(false);
  const [remaining, setRemaining] = useState(5);
  const [conversationId] = useState(newConversationId);
  const [error, setError] = useState<string | null>(null);
  const [landed, setLanded] = useState(0);
  /** Expanded source bodies: `${messageIndex}:${sourceIndex}` */
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>(
    {},
  );

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

  const replyFromData = useCallback(
    (data: Record<string, unknown>): Msg => {
      if (data.kind === "mapping") {
        const irac: Irac = (data.irac as Irac) || {};
        const sources = parseSources(data.sources);
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
          irac.conclusion ? `${t.conclusion}: ${irac.conclusion}` : null,
          verification?.flagged
            ? `${t.verifierNote}: ${verification.confidence_note || t.worthDoubleChecking}`
            : verification
              ? `${t.verifierNote}: ${t.verifyOk}`
              : null,
        ].filter(Boolean);
        return {
          role: "assistant",
          text: parts.join("\n\n"),
          summary: data.summary as string | undefined,
          irac,
          sources,
          verification,
          language: lang,
          engine:
            data.engine === "indictrans2" ||
            data.engine === "ollama_fallback" ||
            data.engine === "unavailable"
              ? data.engine
              : null,
          translationNote:
            typeof data.translation_note === "string" ? data.translation_note : null,
        };
      }
      if (data.kind === "clarify") {
        return {
          role: "assistant",
          text: lang === "en" ? (data.question as string) || t.clarifyFallback : t.clarifyFallback,
          language: lang,
        };
      }
      if (data.kind === "bifurcation") {
        const options = (data.options as BifurcationOption[]) || [];
        return {
          role: "assistant",
          text:
            lang === "en"
              ? (data.prompt as string) || ""
              : t.bifurcationPrompt(options.map((o) => o.section).join(", ")),
          language: lang,
          bifurcationOptions: options,
        };
      }
      if (data.kind === "failure") {
        return {
          role: "assistant",
          text: (data.message as string) || t.failureFallback,
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
      if (!trimmed || busy || remaining <= 0) return;

      setError(null);
      setBusy(true);
      setDraft("");
      setMessages((m) => [...m, { role: "user", text: display ?? trimmed }]);

      try {
        const res = await fetch(`${API_BASE}/api/query`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: trimmed,
            conversation_id: conversationId,
            language: lang,
          }),
        });
        const data = await res.json();
        setMessages((m) => [...m, replyFromData(data)]);
        setRemaining((n) => Math.max(0, n - 1));
      } catch {
        setError(t.apiError);
        setMessages((m) => m.slice(0, -1));
        setDraft(trimmed);
      } finally {
        setBusy(false);
      }
    },
    [busy, conversationId, lang, remaining, replyFromData, t],
  );

  const resolveBifurcation = useCallback(
    async (section: string) => {
      if (!section || busy || remaining <= 0) return;
      setError(null);
      setBusy(true);
      setMessages((m) => [...m, { role: "user", text: section }]);
      try {
        const res = await fetch(`${API_BASE}/api/query/resolve_bifurcation`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            conversation_id: conversationId,
            chosen_section: section,
            language: lang,
          }),
        });
        const data = await res.json();
        setMessages((m) => [...m, replyFromData(data)]);
        setRemaining((n) => Math.max(0, n - 1));
      } catch {
        setError(t.apiError);
        setMessages((m) => m.slice(0, -1));
      } finally {
        setBusy(false);
      }
    },
    [busy, conversationId, lang, remaining, replyFromData, t],
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
      <div className={styles.thread} aria-live="polite" tabIndex={0} data-lenis-prevent>
        {messages.length === 0 ? (
          <div className={styles.empty}>
            <p className={styles.emptyTitle}>{t.emptyTitle}</p>
            <p className={styles.emptyBody}>{t.emptyBody}</p>
            <div className={styles.examples}>
              {EXAMPLES.map((ex) => (
                <button
                  key={ex.en}
                  type="button"
                  className={styles.example}
                  onClick={() => void send(ex.en, ex[lang])}
                  disabled={busy || remaining <= 0}
                  lang={lang}
                >
                  {ex[lang]}
                </button>
              ))}
            </div>
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
                        ["conclusion", t.conclusion, m.irac.conclusion],
                      ] as const
                    ).map(([key, label, value]) =>
                      value ? (
                        <div key={key} className={styles.iracField}>
                          <span className={styles.iracLabel}>{label}</span>
                          <p className={styles.statute}>{value}</p>
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
                                      <p className={styles.sourceText}>{src.text}</p>
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

                    {m.language && m.language !== "en" && m.engine === "indictrans2" ? (
                      <p className={styles.fallbackNote}>{t.machineTranslatedNote}</p>
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
                ) : m.role === "assistant" && m.bifurcationOptions?.length ? (
                  <div className={styles.bifurcation}>
                    <p className={styles.statute}>{m.text}</p>
                    <div className={styles.bifurcationOptions}>
                      {m.bifurcationOptions.map((o) => (
                        <button
                          key={o.section}
                          type="button"
                          className={styles.bifurcationBtn}
                          disabled={busy || remaining <= 0}
                          onClick={() => void resolveBifurcation(o.section)}
                        >
                          <strong>{o.section}</strong>
                          <span>{o.description}</span>
                        </button>
                      ))}
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
          disabled={busy || remaining <= 0}
        />
        <button type="submit" disabled={busy || remaining <= 0 || !draft.trim()}>
          {busy ? t.running : t.send}
        </button>
      </form>

      <p className={styles.note}>{remaining === 1 ? t.freeOne : t.freeMany(remaining)}</p>
      {error ? (
        <p className={styles.error} role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
