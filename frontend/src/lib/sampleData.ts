/**
 * Sample data for the dashboard preview. Every case is one the pipeline was
 * actually run on (PROCESS_LOG §16, §18, §21); statute titles are quoted from
 * data/clean. Dates asked, the offence dates of the evidence-destruction and
 * BNS 26 cases, and the dates "found" in documents are placeholders for the
 * preview.
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

export type SampleDoc = {
  id: string;
  name: string;
  date: string;
  read: "direct" | "ocr" | "pending";
  /** Offence date "found" in the document: a placeholder for the preview. */
  foundDate: string | null;
};

export const SAMPLE_DOCS: SampleDoc[] = [
  { id: "d1", name: "typed-complaint.pdf", date: "2 Oct 2026", read: "direct", foundDate: "5 September 2024" },
  { id: "d2", name: "scanned-notice.jpg", date: "1 Oct 2026", read: "ocr", foundDate: "10 August 2024" },
  { id: "d3", name: "scanned-fir-copy.pdf", date: "29 Sep 2026", read: "ocr", foundDate: "25 June 2024" },
];

export const SAMPLE_EMAIL = "name@example.com";
