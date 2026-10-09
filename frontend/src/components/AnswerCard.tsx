"use client";

import { useId, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { getDictionary, type Dictionary } from "@/lib/i18n";
import { usePrefs, type Lang } from "@/lib/prefs";
import styles from "./ChatEntry.module.css";

export type Irac = {
  issue?: string;
  rule?: string;
  application?: string;
  conclusion?: string;
};

export type Source = {
  statute?: string;
  section?: string;
  text?: string;
};

export type Verification = {
  flagged?: boolean;
  confidence_note?: string;
};

export type OffenseDateUsed = {
  label: string;
  code: "IPC" | "BNS";
  source: "message" | "earlier_message" | "document" | "confirmed";
};

export type FixedConclusionParts = {
  code: string;
  section: string;
  heading: string;
};

export function displayConclusion(
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
export function stripIndexingContext(text: string): string {
  return text.replace(/^\[Context:[^\]]*\]\s*/i, "");
}

export function parseOffenseDateUsed(raw: unknown): OffenseDateUsed | undefined {
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

export function formatOffenseDateUsedLine(
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

export function parseSources(raw: unknown): Source[] {
  if (!Array.isArray(raw)) return [];
  return raw
    .filter((s): s is Record<string, unknown> => !!s && typeof s === "object")
    .map((s) => ({
      statute: typeof s.statute === "string" ? s.statute : undefined,
      section: typeof s.section === "string" ? s.section : undefined,
      text: typeof s.text === "string" ? s.text : undefined,
    }));
}

export function parseVerification(raw: unknown): Verification | null {
  if (!raw || typeof raw !== "object") return null;
  const v = raw as Record<string, unknown>;
  return {
    flagged: Boolean(v.flagged),
    confidence_note:
      typeof v.confidence_note === "string" ? v.confidence_note : undefined,
  };
}

export function parseFixedConclusion(raw: unknown): FixedConclusionParts | undefined {
  if (!raw || typeof raw !== "object") return undefined;
  const o = raw as Record<string, unknown>;
  if (typeof o.code !== "string" || typeof o.section !== "string") return undefined;
  return {
    code: o.code,
    section: o.section,
    heading: typeof o.heading === "string" ? o.heading : "",
  };
}

export function CheckIcon() {
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

export function FlagIcon() {
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


export type CardData = {
  summary?: string;
  irac?: Irac;
  sources?: Source[];
  verification?: Verification | null;
  language?: string;
  engine?: "indictrans2" | "ollama_fallback" | "unavailable" | null;
  translationNote?: string | null;
  translationFallbackFields?: string[] | null;
  offenseDateUsed?: OffenseDateUsed;
  fixedConclusion?: FixedConclusionParts;
  ruleTruncated?: boolean;
  showExceptionNotice?: boolean;
  showScope?: boolean;
};

/**
 * One mapped answer: Issue, Rule (statute text), the collapsed generated Application, Conclusion,
 * sources, the verification line and the notices. Used by the chat and by a saved History answer.
 * `lang` overrides the reader's language (a saved answer keeps the language it was written in).
 */
export function AnswerCard({ card: c, lang: langProp }: { card: CardData; lang?: Lang }) {
  const prefs = usePrefs();
  const lang = langProp ?? prefs.lang;
  const t = langProp ? getDictionary(langProp) : prefs.t;
  const reduceMotion = useReducedMotion();
  const uid = useId();
  const [showApp, setShowApp] = useState(false);
  const [openSrc, setOpenSrc] = useState<Record<string, boolean>>({});
  if (!c.irac) return null;
  return (
                  <div className={styles.iracBlock}>
                    {c.offenseDateUsed ? (
                      <p className={styles.displayMeta}>
                        {formatOffenseDateUsedLine(c.offenseDateUsed, lang, t)}
                      </p>
                    ) : null}
                    {c.summary ? (
                      <p className={styles.summaryLine}>
                        {t.mapped}: {c.summary}
                      </p>
                    ) : null}
                    {(
                      [
                        ["issue", t.issue, c.irac.issue],
                        ["rule", t.ruleStatute, c.irac.rule],
                        ["application", t.application, c.irac.application],
                        [
                          "conclusion",
                          t.conclusion,
                          // Prefer the localised template from structured parts
                          // so HI/MR (and language switches) do not show the
                          // English fixed sentence baked at reply time.
                          displayConclusion(c.irac, c.fixedConclusion, lang, t) ??
                            c.irac.conclusion,
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
                              <>
                                <button
                                  type="button"
                                  className={styles.appToggle}
                                  aria-expanded={showApp}
                                  aria-controls={`${uid}-app`}
                                  onClick={() => setShowApp((v) => !v)}
                                >
                                  {showApp ? t.hideApplication : t.showApplication}
                                </button>
                                {showApp ? (
                                  <div id={`${uid}-app`}>
                                    <p className={styles.generatedNote}>
                                      {t.generatedNote}
                                    </p>
                                    <p className={styles.statute}>{value}</p>
                                  </div>
                                ) : null}
                              </>
                            ) : (
                              <>
                                <p className={styles.statute}>{value}</p>
                                {key === "rule" &&
                                ((c.language && c.language !== "en") || c.ruleTruncated) ? (
                                  <p className={styles.generatedNote}>
                                    {[
                                      c.language && c.language !== "en" ? t.statuteInEnglish : null,
                                      c.ruleTruncated ? t.ruleTruncated : null,
                                    ]
                                      .filter(Boolean)
                                      .join(" ")}
                                  </p>
                                ) : null}
                              </>
                            )}
                          </div>
                        </div>
                      ) : null,
                    )}

                    {c.sources && c.sources.length > 0 ? (
                      <div className={styles.sourcesBlock}>
                        <span className={styles.iracLabel}>
                          {t.sourcesHeading(c.sources.length)}
                        </span>
                        <ul className={styles.sourcesList}>
                          {c.sources.map((src, si) => {
                            const key = String(si);
                            const open = Boolean(openSrc[key]);
                            const cite = [src.statute, src.section]
                              .filter(Boolean)
                              .join(" ");
                            return (
                              <li key={key} className={styles.sourceItem}>
                                <button
                                  type="button"
                                  className={styles.sourceToggle}
                                  aria-expanded={open}
                                  onClick={() => setOpenSrc((p) => ({ ...p, [key]: !p[key] }))}
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

                    {c.verification ? (
                      <div
                        className={
                          c.verification.flagged ? styles.verifyFlagged : styles.verifyOk
                        }
                        role="status"
                      >
                        {c.verification.flagged ? (
                          <>
                            <span className={styles.verifyMark}>
                              <FlagIcon />
                            </span>
                            <div>
                              <strong>{t.worthDoubleChecking}</strong>
                              {c.verification.confidence_note ? (
                                <p className={styles.verifyNote}>
                                  {c.verification.confidence_note}
                                </p>
                              ) : null}
                            </div>
                          </>
                        ) : (
                          <>
                            <span className={styles.verifyMark}>
                              <CheckIcon />
                            </span>
                            <span>{c.verification.confidence_note || t.verifyOk}</span>
                          </>
                        )}
                      </div>
                    ) : null}

                    {c.showScope ? (
                      <p className={styles.displayMeta}>{t.scopeLine}</p>
                    ) : null}
                    {c.showExceptionNotice ? (
                      <p className={styles.displayMeta}>{t.exceptionProvisoNotice}</p>
                    ) : null}

                    {c.language && c.language !== "en" && c.engine === "indictrans2" ? (
                      <p className={styles.fallbackNote}>{t.machineTranslatedNote}</p>
                    ) : null}
                    {c.translationFallbackFields &&
                    c.translationFallbackFields.length > 0 ? (
                      <p className={styles.fallbackNote}>
                        {t.numberGuardFallbackNote}
                      </p>
                    ) : null}
                    {c.engine === "ollama_fallback" ? (
                      <p className={styles.fallbackNote}>
                        {c.translationNote || t.translationFallbackNote}
                      </p>
                    ) : null}
                    {c.engine === "unavailable" && c.translationNote ? (
                      <p className={styles.fallbackNote}>{c.translationNote}</p>
                    ) : null}
                  </div>
  );
}

/** Version 1 of the answer stored with a History row (the `result` jsonb column). */
export type SavedResult = {
  v: 1;
  card: CardData;
  meta: { code: string; section: string; heading: string | null; offence_date: string | null; date_source: string | null };
};

/** Builds the stored form of a finished answer card. Plain data only. */
export function toSavedResult(card: CardData, meta: SavedResult["meta"]): SavedResult {
  const { summary, irac, sources, verification, language, engine, translationNote, translationFallbackFields } = card;
  const { offenseDateUsed, fixedConclusion, ruleTruncated, showExceptionNotice, showScope } = card;
  return {
    v: 1,
    card: {
      summary, irac, sources, verification, language, engine, translationNote, translationFallbackFields,
      offenseDateUsed, fixedConclusion, ruleTruncated, showExceptionNotice, showScope,
    },
    meta,
  };
}

const str = (v: unknown) => (typeof v === "string" ? v : undefined);

/** Reads a stored answer back, trusting nothing: every field is type-checked. Null when it is not a v1 answer. */
export function parseSavedResult(raw: unknown): CardData | null {
  if (!raw || typeof raw !== "object") return null;
  const r = raw as Record<string, unknown>;
  if (r.v !== 1 || !r.card || typeof r.card !== "object") return null;
  const c = r.card as Record<string, unknown>;
  const i = c.irac && typeof c.irac === "object" ? (c.irac as Record<string, unknown>) : null;
  if (!i) return null;
  const irac: Irac = { issue: str(i.issue), rule: str(i.rule), application: str(i.application), conclusion: str(i.conclusion) };
  if (!irac.rule && !irac.issue && !irac.conclusion) return null;
  const language = c.language === "hi" || c.language === "mr" || c.language === "en" ? c.language : "en";
  const engine =
    c.engine === "indictrans2" || c.engine === "ollama_fallback" || c.engine === "unavailable" ? c.engine : null;
  return {
    summary: str(c.summary),
    irac,
    sources: parseSources(c.sources),
    verification: parseVerification(c.verification),
    language,
    engine,
    translationNote: str(c.translationNote) ?? null,
    translationFallbackFields: Array.isArray(c.translationFallbackFields)
      ? c.translationFallbackFields.filter((x): x is string => typeof x === "string")
      : null,
    offenseDateUsed: parseOffenseDateUsed(c.offenseDateUsed),
    fixedConclusion: parseFixedConclusion(c.fixedConclusion),
    ruleTruncated: c.ruleTruncated === true,
    showExceptionNotice: c.showExceptionNotice === true,
    showScope: c.showScope === true,
  };
}
