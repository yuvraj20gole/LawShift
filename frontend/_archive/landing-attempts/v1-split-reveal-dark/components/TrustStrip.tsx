"use client";

import Link from "next/link";
import { Reveal } from "./Reveal";
import { useT } from "@/lib/prefs";
import styles from "./TrustStrip.module.css";

export function TrustStrip() {
  const t = useT();
  const cards = [
    { title: t.trustCard1Title, body: t.trustCard1Body },
    { title: t.trustCard2Title, body: t.trustCard2Body },
    { title: t.trustCard3Title, body: t.trustCard3Body },
  ];

  return (
    <section className={styles.section} aria-label={t.trustAria}>
      <div className="container">
        <div className={styles.grid}>
          {cards.map((c, i) => (
            <Reveal key={c.title} index={i} as="article" className={styles.card}>
              <p className={styles.title}>{c.title}</p>
              <p className={styles.body}>{c.body}</p>
            </Reveal>
          ))}
        </div>
        <p className={styles.caption}>
          <Link href="/about" className={styles.evalLink}>
            {t.trustEvalLink}
          </Link>
        </p>
      </div>
    </section>
  );
}
