/**
 * Sample data for the dashboard preview. Every case is one the pipeline was
 * actually run on (PROCESS_LOG §16, §18, §21); statute titles and excerpts
 * are quoted from data/clean. Dates asked, and the offence date of the
 * evidence-destruction and BNS 26 cases, are placeholders for the preview.
 */
export type Code = "IPC" | "BNS";

export type SampleCase = {
  id: string;
  asked: string;
  offence: string;
  code: Code;
  section: string;
  title: string;
  flagged: boolean;
  question: string;
};

export const SAMPLE_CASES: SampleCase[] = [
  {
    id: "c5",
    asked: "2 Oct 2026",
    offence: "5 Sep 2024",
    code: "BNS",
    section: "180",
    title: "Possession of forged or counterfeit coin, Government stamp, currency-notes or bank-notes",
    flagged: false,
    question: "A person was found in possession of counterfeit currency notes.",
  },
  {
    id: "c4",
    asked: "2 Oct 2026",
    offence: "10 Aug 2024",
    code: "BNS",
    section: "193",
    title: "Liability of owner, occupier, etc., of land on which an unlawful assembly or riot takes place",
    flagged: false,
    question: "A riot occurred for a landowner’s benefit and the agent failed to prevent it.",
  },
  {
    id: "c3",
    asked: "1 Oct 2026",
    offence: "25 Jun 2024",
    code: "IPC",
    section: "292",
    title: "Sale, etc., of obscene books, etc.",
    flagged: false,
    question: "A bookstore owner sold obscene magazines for the first time.",
  },
  {
    id: "c2",
    asked: "30 Sep 2026",
    offence: "12 Mar 2024",
    code: "IPC",
    section: "201",
    title: "Causing disappearance of evidence of offence, or giving false information to screen offender",
    flagged: false,
    question: "Evidence of an offence was destroyed to screen the offender.",
  },
  {
    id: "c1",
    asked: "29 Sep 2026",
    offence: "15 Sep 2024",
    code: "BNS",
    section: "26",
    title: "Act not intended to cause death, done by consent in good faith for person’s benefit",
    flagged: true,
    question: "A euthanasia question where the written conclusion did not follow the rule.",
  },
];

export type SampleSaved = {
  id: string;
  code: Code;
  section: string;
  title: string;
  excerpt: string;
  saved: string;
};

export const SAMPLE_SAVED: SampleSaved[] = [
  {
    id: "s1",
    code: "BNS",
    section: "193",
    title: "Liability of owner, occupier, etc., of land on which an unlawful assembly or riot takes place",
    excerpt:
      "Whenever any unlawful assembly or riot takes place, the owner or occupier of the land upon which such unlawful assembly is held, or such riot is committed, and any person having or claiming an interest in …",
    saved: "2 Oct 2026",
  },
  {
    id: "s2",
    code: "BNS",
    section: "180",
    title: "Possession of forged or counterfeit coin, Government stamp, currency-notes or bank-notes",
    excerpt:
      "Whoever has in his possession any forged or counterfeit coin, stamp, currency-note or bank-note, knowing or having reason to believe the same to be forged or counterfeit …",
    saved: "2 Oct 2026",
  },
  {
    id: "s3",
    code: "IPC",
    section: "292",
    title: "Sale, etc., of obscene books, etc.",
    excerpt:
      "Whoever (a) sells, lets to hire, distributes, publicly exhibits or in any manner puts into circulation, or for purposes of sale, hire, distribution, public exhibition or circulation, makes, produces or has in his possession any obscene book …",
    saved: "1 Oct 2026",
  },
  {
    id: "s4",
    code: "IPC",
    section: "201",
    title: "Causing disappearance of evidence of offence, or giving false information to screen offender",
    excerpt:
      "Whoever, knowing or having reason to believe that an offence has been committed, causes any evidence of the commission of that offence to disappear, with the intention of screening the offender from legal punishment …",
    saved: "30 Sep 2026",
  },
];

export type SampleDoc = {
  id: string;
  name: string;
  date: string;
  read: "direct" | "ocr" | "pending";
};

export const SAMPLE_DOCS: SampleDoc[] = [
  { id: "d1", name: "typed-complaint.pdf", date: "2 Oct 2026", read: "direct" },
  { id: "d2", name: "scanned-notice.jpg", date: "1 Oct 2026", read: "ocr" },
  { id: "d3", name: "scanned-fir-copy.pdf", date: "29 Sep 2026", read: "ocr" },
];

export const SAMPLE_EMAIL = "name@example.com";
export const QUESTIONS_TOTAL = 5;
export const SAMPLE_QUESTIONS_LEFT = 3;
