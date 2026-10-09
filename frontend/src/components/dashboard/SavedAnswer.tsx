"use client";

import { AnswerCard, type CardData } from "@/components/AnswerCard";
import { usePrefs } from "@/lib/prefs";
import { getDictionary } from "@/lib/i18n";
import { getDashboardCopy } from "@/lib/dashboardCopy";
import chat from "@/components/ChatEntry.module.css";
import d from "./dashboard.module.css";
import styles from "./savedAnswer.module.css";

const LOCALES = { en: "en-GB", hi: "hi-IN", mr: "mr-IN" } as const;

type Props = {
  question: string;
  card: CardData;
  createdAt: string;
  onFollowUp: () => void;
  onRunAgain: () => void;
  busy?: boolean;
};

/**
 * A saved History answer, read only: the original question, the answer card in the language it was
 * saved in, a line saying it was not re-run, and the two ways to carry on. Page text follows the
 * reader's language; the question and the card keep the saved one.
 */
export function SavedAnswer({ question, card, createdAt, onFollowUp, onRunAgain, busy }: Props) {
  const { lang } = usePrefs();
  const C = getDashboardCopy(lang);
  const saved = (card.language === "hi" || card.language === "mr" ? card.language : "en") as "en" | "hi" | "mr";
  const T = getDictionary(saved);
  const when = new Date(createdAt);
  const date = Number.isNaN(when.getTime())
    ? ""
    : when.toLocaleDateString(LOCALES[lang] ?? "en-GB", { day: "numeric", month: "long", year: "numeric" });

  return (
    <section className={styles.saved} aria-label={C.savedFrom(date)}>
      <div lang={saved}>
        <div className={chat.user}>
          <span className={chat.role}>{T.you}</span>
          <p>{question}</p>
        </div>
        <div className={`${chat.assistant} ${styles.answer}`}>
          <span className={chat.role}>{T.assistant}</span>
          <AnswerCard card={card} lang={saved} />
        </div>
      </div>
      <p className={d.note}>{C.savedFrom(date)}</p>
      <div className={styles.actions}>
        <button type="button" className={d.primary} onClick={onFollowUp} disabled={busy}>
          {C.savedFollowUp}
        </button>
        <button type="button" className={d.secondary} onClick={onRunAgain} disabled={busy}>
          {C.savedRunAgain}
        </button>
      </div>
    </section>
  );
}
