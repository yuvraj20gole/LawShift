"use client";

import { useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { Reveal } from "./Reveal";
import { useT } from "@/lib/prefs";
import styles from "./FAQ.module.css";

export function FAQ() {
  const t = useT();
  const reduce = useReducedMotion();
  const [open, setOpen] = useState<number | null>(0);
  const items = [
    { q: t.faqQ1, a: t.faqA1 },
    { q: t.faqQ2, a: t.faqA2 },
    { q: t.faqQ3, a: t.faqA3 },
    { q: t.faqQ4, a: t.faqA4 },
  ];

  return (
    <section className={styles.section} aria-labelledby="faq-heading">
      <div className="container">
        <Reveal>
          <h2 id="faq-heading" className={styles.heading}>
            {t.faqHeading}
          </h2>
        </Reveal>
        <Reveal index={1}>
          <div className={styles.list}>
            {items.map((item, i) => {
              const isOpen = open === i;
              return (
                <div key={item.q} className={styles.item}>
                  <button
                    type="button"
                    className={styles.trigger}
                    aria-expanded={isOpen}
                    onClick={() => setOpen(isOpen ? null : i)}
                  >
                    <span>{item.q}</span>
                    <span className={styles.chev} aria-hidden="true">
                      {isOpen ? "−" : "+"}
                    </span>
                  </button>
                  <AnimatePresence initial={false}>
                    {isOpen ? (
                      <motion.div
                        key="answer"
                        className={styles.answerWrap}
                        initial={
                          reduce
                            ? { opacity: 0 }
                            : { height: 0, opacity: 0 }
                        }
                        animate={
                          reduce
                            ? { opacity: 1 }
                            : { height: "auto", opacity: 1 }
                        }
                        exit={
                          reduce
                            ? { opacity: 0 }
                            : { height: 0, opacity: 0 }
                        }
                        transition={
                          reduce
                            ? { duration: 0.12 }
                            : {
                                height: {
                                  duration: 0.22,
                                  ease: [0.22, 1, 0.36, 1],
                                },
                                opacity: { duration: 0.16, ease: "easeOut" },
                              }
                        }
                      >
                        <p className={styles.answer}>{item.a}</p>
                      </motion.div>
                    ) : null}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
