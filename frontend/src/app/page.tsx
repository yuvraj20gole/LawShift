"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Header } from "@/components/Header";
import { ChatEntry } from "@/components/ChatEntry";
import { Docket } from "@/components/Docket";
import { Compare } from "@/components/Compare";
import { Waffle } from "@/components/Waffle";
import { CheckerStrip } from "@/components/CheckerStrip";
import { Rise } from "@/components/Rise";
import { ScrubRail } from "@/components/ScrubRail";
import { SplitText } from "@/components/SplitText";
import { CountUp } from "@/components/CountUp";
import { Curtain } from "@/components/Curtain";
import { Parallax } from "@/components/Parallax";
import { CalendarIcon, CheckPageIcon, ForkIcon, SearchIcon } from "@/components/StepIcons";
import { usePrefs } from "@/lib/prefs";
import { getLandingCopy } from "@/lib/landingCopy";
import styles from "./landing.module.css";

export default function HomePage() {
  const { lang } = usePrefs();
  const L = getLandingCopy(lang);

  // Reload was restoring the previous mid-page scroll (e.g. "What happens"),
  // so the hero never showed. Manual restoration: top on bare `/`, keep
  // intentional hash targets like /#how and /#chat.
  useEffect(() => {
    if ("scrollRestoration" in history) {
      history.scrollRestoration = "manual";
    }
    if (!window.location.hash) {
      window.scrollTo(0, 0);
    }
  }, []);

  const steps = [
    { title: L.step1Title, who: L.step1Who, body: L.step1Body, Icon: CalendarIcon },
    { title: L.step2Title, who: L.step2Who, body: L.step2Body, Icon: ForkIcon },
    { title: L.step3Title, who: L.step3Who, body: L.step3Body, Icon: SearchIcon },
    { title: L.step4Title, who: L.step4Who, body: L.step4Body, Icon: CheckPageIcon },
  ];

  const outcomes = [
    { when: L.outcome1When, then: L.outcome1Then },
    { when: L.outcome2When, then: L.outcome2Then },
    { when: L.outcome3When, then: L.outcome3Then },
    { when: L.outcome4When, then: L.outcome4Then },
  ];

                  const evidence = [
    {
      asked: L.evidence1Asked,
      result: L.evidence1Result,
      fine: L.evidence1Fine,
      kind: "figure" as const,
      figure: L.evidence1Fig,
    },
    {
      asked: L.evidence2Asked,
      result: L.evidence2Result,
      fine: L.evidence2Fine,
      kind: "waffle" as const,
    },
    {
      asked: L.evidence3Asked,
      result: L.evidence3Result,
      fine: L.evidence3Fine,
      kind: "figure" as const,
      figure: L.evidence3Fig,
    },
  ];

  const limits = [
    { title: L.limit1Title, body: L.limit1Body },
    { title: L.limit2Title, body: L.limit2Body },
    { title: L.limit3Title, body: L.limit3Body },
    { title: L.limit4Title, body: L.limit4Body },
  ];

  return (
    <>
      <a href="#main" className={styles.skip}>
        {L.skipLink}
      </a>
      <Header />
      <main id="main">
        <section className={styles.hero} aria-labelledby="hero-title">
          <div className="container">
            <div className={styles.heroGrid}>
              <Parallax className={styles.heroText} from={0} to={-70}>
                <h1 id="hero-title" className={styles.h1}>
                  <SplitText immediate text={L.heroTitle} />
                </h1>
                <p className={styles.lead}>{L.heroLead}</p>
                <div className={styles.actions}>
                  <Link href="#chat" className={styles.primary}>
                    {L.heroCta}
                  </Link>
                  <Link href="#checks" className={styles.textLink}>
                    {L.heroChecks}
                  </Link>
                </div>
                <p className={styles.audience}>{L.audience}</p>
              </Parallax>
              <Parallax from={0} to={45}>
                <Docket />
              </Parallax>
            </div>
          </div>
        </section>

        <Curtain
          id="chat"
          className={`${styles.band} ${styles.chatBand}`}
          labelledBy="chat-title"
        >
          <div className="container">
            <div className={styles.chatIntro}>
              <SplitText as="p" className={styles.bigLine} text={L.chatLead} />
              <ul className={styles.tips}>
                <li>{L.chatTip1}</li>
                <li>{L.chatTip2}</li>
                <li>{L.chatTip3}</li>
              </ul>
            </div>
            <div className={styles.bandGrid}>
              <Rise className={`${styles.margin} ${styles.chatMargin}`}>
                <h2 id="chat-title" className={styles.h2}>
                  {L.chatTitle}
                </h2>
              </Rise>
              <div className={styles.chatBody}>
                <div className={styles.chatShell}>
                  <ChatEntry />
                </div>
              </div>
            </div>
          </div>
        </Curtain>

        <section
          id="how"
          className={`${styles.band} ${styles.bandDim} ${styles.afterChat}`}
          aria-labelledby="how-title"
        >
          <div className="container">
            <SplitText as="p" className={styles.bigLine} text={L.howLead} />
            <div className={styles.bandGrid}>
              <Rise className={styles.margin}>
                <h2 id="how-title" className={styles.h2}>
                  {L.howTitle}
                </h2>
              </Rise>
              <div className={styles.body}>
                <ScrubRail
                              steps={steps.map((s) => (
                                <>
                                  <s.Icon className={styles.stepIcon} />
                                  <h3 className={styles.h3}>{s.title}</h3>
                                  <p className={styles.who}>{s.who}</p>
                                  <p className={styles.stepBody}>{s.body}</p>
                                </>
                              ))}
                            />
              </div>
            </div>
          </div>
        </section>

        <section
          id="compare"
          className={styles.band}
          aria-labelledby="compare-title"
        >
          <div className="container">
            <SplitText as="p" className={styles.bigLine} text={L.compareLead} />
            <div className={styles.bandGrid}>
              <Rise className={styles.margin}>
                <h2 id="compare-title" className={styles.h2}>
                  {L.compareTitle}
                </h2>
              </Rise>
              <div className={styles.compareBody}>
                <Compare />
              </div>
            </div>
          </div>
        </section>

        <section id="checks" className={`${styles.band} ${styles.bandDim}`} aria-labelledby="checks-title">
          <div className="container">
            <SplitText as="p" className={styles.bigLine} text={L.checksLead} />
            <div className={styles.bandGrid}>
              <Rise className={styles.margin}>
                <h2 id="checks-title" className={styles.h2}>
                  {L.checksTitle}
                </h2>
              </Rise>
              <div className={styles.body}>
                <dl className={styles.outcomes}>
                  {outcomes.map((o, i) => (
                    <Rise
                      key={o.when}
                      index={i}
                      className={`${styles.outcome} ${
                        i === 2 ? styles.outcomeSeam : i === 3 ? styles.outcomeOk : ""
                      }`}
                    >
                      <dt>{o.when}</dt>
                      <dd>{o.then}</dd>
                    </Rise>
                  ))}
                </dl>
                <Rise className={styles.aside}>
                  <h3 className={styles.h3}>{L.checkerTitle}</h3>
                  <p>{L.checkerP1}</p>
                  <p>{L.checkerP2}</p>
                  <CheckerStrip
                    title={L.stripTitle}
                    caught={L.stripCaught}
                    falseAlarm={L.stripFalse}
                    clear={L.stripClear}
                  />
                </Rise>
              </div>
            </div>
          </div>
        </section>

        <section
          id="evidence"
          className={styles.band}
          aria-labelledby="evidence-title"
        >
          <div className="container">
            <SplitText as="p" className={styles.bigLine} text={L.evidenceLead} />
            <div className={styles.bandGrid}>
              <Rise className={styles.margin}>
                <h2 id="evidence-title" className={styles.h2}>
                  {L.evidenceTitle}
                </h2>
              </Rise>
              <div className={styles.body}>
                <div className={styles.evidence}>
                  {evidence.map((e) => (
                    <Rise as="article" key={e.asked} className={styles.evRow}>
                      <div className={styles.evViz}>
                        {e.kind === "waffle" ? (
                          <div className={styles.waffles}>
                            <Waffle
                              hit={84}
                              label={L.waffleLabelA}
                              figure={L.waffleFigA}
                              hitLabel={L.waffleHit}
                              missLabel={L.waffleMiss}
                            />
                            <Waffle
                              hit={66}
                              label={L.waffleLabelB}
                              figure={L.waffleFigB}
                              hitLabel={L.waffleHit}
                              missLabel={L.waffleMiss}
                            />
                          </div>
                        ) : (
                          <p className={styles.bigFigure}>
                            <CountUp text={e.figure ?? ""} />
                          </p>
                        )}
                      </div>
                      <div className={styles.evText}>
                        <h3 className={styles.h3}>{e.asked}</h3>
                        <p className={styles.evResult}>{e.result}</p>
                        <p className={styles.evFine}>{e.fine}</p>
                      </div>
                    </Rise>
                  ))}
                </div>
                <p className={styles.more}>
                  {L.evidenceMoreBefore}{" "}
                  <Link href="/about">{L.evidenceMoreLink}</Link>.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section
          id="limits"
          className={`${styles.band} ${styles.bandSunken}`}
          aria-labelledby="limits-title"
        >
          <div className="container">
            <div className={styles.bandGrid}>
              <Rise className={styles.margin}>
                <h2 id="limits-title" className={styles.h2}>
                  {L.limitsTitle}
                </h2>
              </Rise>
              <div className={styles.body}>
                <dl className={styles.limits}>
                  {limits.map((l, i) => (
                    <Rise key={l.title} index={i} className={styles.limit}>
                      <dt>{l.title}</dt>
                      <dd>{l.body}</dd>
                    </Rise>
                  ))}
                </dl>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className={styles.footer}>
        <div className="container">
          <div className={styles.bandGrid}>
            <div className={`${styles.margin} ${styles.footMark}`}>
              <p className={styles.mark}>LawShift</p>
              <nav className={styles.footNav} aria-label="Footer">
                <Link href="#chat">{L.tryACase}</Link>
                <Link href="#how">{L.navHow}</Link>
                <Link href="#evidence">{L.navEvidence}</Link>
                <Link href="/about">{L.navAbout}</Link>
              </nav>
            </div>
            <div className={styles.body}>
              <p className={styles.disclaimer}>{L.footerDisclaimer}</p>
              <p className={styles.credits}>{L.footerCredits}</p>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}
