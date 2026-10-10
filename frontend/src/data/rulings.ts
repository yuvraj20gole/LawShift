/**
 * Background judgments on which code applies to an offence committed before
 * 1 July 2024. Used as the Overview fallback when the archive route can't be
 * reached, and shown as the "Background" group on the Rulings page (next pass).
 *
 * Every field below was read from the judgment PDF itself on `reviewedOn`
 * (copies hosted by LiveLaw, livelaw.in, not the courts' own sites, so
 * linkKind is "other"). Nothing was filled from memory. All entries are still
 * `verified: false`: a person has not yet checked them against the courts'
 * own copies, so the UI shows a "Draft: not yet checked" badge.
 *
 * A field that could not be settled from the text says "to verify".
 */
export type RulingEntry = {
  court: string;
  /** ISO date, or "to verify". */
  decidedOn: string;
  title: string;
  /** Plain-language statement of what the court held, with paragraph numbers. */
  holding: string;
  url: string;
  /**
   * "court": the court's own site. "archive": a public judgment archive.
   * "other": any other site (a news or law-reporting site); name it in siteName.
   * Set from the url's domain, not by assumption.
   */
  linkKind: "court" | "archive" | "other";
  /** Site name for linkKind "other", for example "LiveLaw". */
  siteName?: string;
  /** "featured" (recent Supreme Court judgments) or "background" (which code applies). */
  group: "featured" | "background";
  branch: "criminal" | "civil";
  topic?: "ipc-bns";
  /** Where the text was read, and any caveat about it. */
  source: string;
  reviewedOn: string;
  verified: boolean;
  caseNumber?: string;
};

export const BACKGROUND_RULINGS: RulingEntry[] = [
  {
    court: "Rajasthan High Court",
    // The head of the order prints 21/08/2024, but the order also cites a
    // Rajasthan High Court decision dated 09.09.2024 (fn 1, Krishna Joshi),
    // so 21/08/2024 cannot be the date it was pronounced.
    decidedOn: "to verify",
    title: "Vijay Sharma & Anr. v. State of Rajasthan & Anr.",
    caseNumber: "S.B. Criminal Misc. (Pet.) No. 5522/2024; 2024:RJ-JD:35171; Arun Monga J.",
    holding:
      "An FIR for an offence committed before 1 July 2024 has to be registered under the IPC even if it is registered after the BNS came into force, and cannot be registered under the BNS (paras 14, 18). For such an FIR the procedure is the BNSS, not the CrPC (para 24). The FIR was quashed on its merits.",
    url: "https://www.livelaw.in/pdf_upload/vijay-sharma-reportable-judgment-5522-2024-563399.pdf",
    linkKind: "other",
    siteName: "LiveLaw",
    group: "background",
    branch: "criminal",
    topic: "ipc-bns",
    source:
      "Read from the judgment PDF (LiveLaw copy). The printed order date, 21/08/2024, conflicts with a 09.09.2024 decision the judgment itself cites, so the pronouncement date is not settled here.",
    reviewedOn: "2026-10-04",
    verified: false,
  },
  {
    court: "Allahabad High Court",
    decidedOn: "2024-08-06",
    title: "Deepu and 4 Others v. State of U.P. and 3 Others",
    caseNumber:
      "Criminal Misc. Writ Petition No. 12287 of 2024; 2024:AHC:126843-DB; Vivek Kumar Birla and Arun Kumar Singh Deshwal JJ.",
    holding:
      "If an FIR is registered on or after 1 July 2024 for an offence committed before it, the FIR is registered under the IPC but the investigation continues under the BNSS (para 16(i)). A pending investigation stays under the CrPC until cognizance is taken on the police report (para 16(ii)).",
    url: "https://www.livelaw.in/pdf_upload/deepu-and-4-others-vs-state-of-up-and-3-others-2024-livelaw-ab-517-allahabad-high-court-555989.pdf",
    linkKind: "other",
    siteName: "LiveLaw",
    group: "background",
    branch: "criminal",
    topic: "ipc-bns",
    source:
      "Read from the judgment PDF (LiveLaw copy). Date taken from 'Order Date : 06.08.2024' at its end.",
    reviewedOn: "2026-10-04",
    verified: false,
  },
  {
    court: "Madras High Court",
    decidedOn: "2024-10-25",
    title: "Muthuvelaydha Perumal Appavu @ M. Appavu v. R.M. Babu Murugavel",
    caseNumber:
      "Crl.O.P. No. 25334 of 2024 with Crl.M.P. Nos. 14210 and 14212 of 2024; Dr. G. Jayachandran J.",
    holding:
      "For the procedure to follow for an offence committed before 1 July 2024, the CrPC 1973 alone applies, in view of section 4 and section 531(2)(a) of the BNSS (para 15). Reading the saving clause as covering only matters already pending would run against the savings in section 358 of the BNS and the General Clauses Act (para 17). This differs in outcome from Deepu above, which sends the investigation of a post-1 July FIR to the BNSS. The judgment cites Deepu only in the petitioner's argument (para 4) and does not discuss it by name in its reasoning.",
    url: "https://www.livelaw.in/pdf_upload/appavu-v-babu-murugavel-568061.pdf",
    linkKind: "other",
    siteName: "LiveLaw",
    group: "background",
    branch: "criminal",
    topic: "ipc-bns",
    source:
      "Read from the judgment PDF (LiveLaw copy). Printed: reserved 22.10.2024, pronounced 25.10.2024. No neutral citation is printed on the copy read.",
    reviewedOn: "2026-10-04",
    verified: false,
  },
];

/**
 * Featured: recent Supreme Court judgments, read from the court's own PDFs
 * (sci.gov.in) on 4 October 2026: the newest three criminal and three civil
 * judgments listed under Judgments on its homepage, after skipping anything
 * involving minors, POCSO or sexual offences (Santosh Gurung v. State of
 * Sikkim and State of H.P. v. Anchla were skipped on that rule). Holdings are
 * my own summaries of the judgment text; all are unverified drafts.
 */
export const FEATURED_RULINGS: RulingEntry[] = [
  {
    court: "Supreme Court of India",
    decidedOn: "2026-09-30",
    title: "Sainaba v. State of Kerala & Anr.",
    caseNumber: "Criminal Appeal arising out of SLP (Crl.) No. 17180 of 2025 (listed by the court as Crl.A. No. 4640/2026); 2026 INSC 1069; Ahsanuddin Amanullah and Manmohan JJ.",
    holding:
      "For the cheque-bounce offence (section 138, Negotiable Instruments Act), the demand notice counts as given once it is sent to the drawer's correct address. It need not be handed to the drawer in person: here his mother received it. It is for the drawer to show the address was wrong or that he knew nothing of the notice (paras 33-35). The Supreme Court restored the conviction.",
    url: "https://www.sci.gov.in/view-pdf/?diary_no=612692025&type=j&order_date=2026-09-30&from=latest_judgements_order",
    linkKind: "court",
    group: "featured",
    branch: "criminal",
    source:
      "Read from the PDF served by sci.gov.in (listed under Judgments on the court's homepage) on 4 October 2026. Holding written from the judgment itself, not from the court's summary.",
    reviewedOn: "2026-10-04",
    verified: false,
  },
  {
    court: "Supreme Court of India",
    decidedOn: "2026-09-29",
    title: "Saurabh Bajaj v. State of Chhattisgarh & Ors.",
    caseNumber: "Criminal Appeal @ SLP (Crl.) No. 16871 of 2026 (listed by the court as Crl.A. No. 4666/2026); 2026 INSC 1076; J.B. Pardiwala and K. Vinod Chandran JJ.",
    holding:
      "A conviction for transporting cattle under the Chhattisgarh Agricultural Cattle Preservation Act, 2004 was set aside. The Act's reversal of the burden of proof (section 11) applies only after the prosecution proves the basic ingredients. Missing transport papers do not by themselves show the cattle were being moved for slaughter, and the veterinary doctor and the gaushala president said the animals were fit for farm work (paras 8-9).",
    url: "https://www.sci.gov.in/view-pdf/?diary_no=425932026&type=j&order_date=2026-09-29&from=latest_judgements_order",
    linkKind: "court",
    group: "featured",
    branch: "criminal",
    source:
      "Read from the PDF served by sci.gov.in (listed under Judgments on the court's homepage) on 4 October 2026. Holding written from the judgment itself, not from the court's summary.",
    reviewedOn: "2026-10-04",
    verified: false,
  },
  {
    court: "Supreme Court of India",
    decidedOn: "2026-09-29",
    title: "Mulla Afroz v. Union of India & Ors.",
    caseNumber: "Criminal Appeal No. 4310 of 2026 (arising out of SLP (Crl.) No. 12534 of 2026); 2026 INSC 1067; Dipankar Datta and Sheel Nagu JJ.",
    holding:
      "A preventive detention order under the National Security Act, 1980 was set aside. Where the detention rests on the same incident and largely the same material as pending criminal cases, it can become punitive rather than preventive. It must show a need to prevent future conduct, and gets closer scrutiny (paras 64-65). The Court gave no view on the criminal cases and awarded Rs 10 lakh costs against the State (paras 66, 69).",
    url: "https://www.sci.gov.in/view-pdf/?diary_no=374372026&type=j&order_date=2026-09-29&from=latest_judgements_order",
    linkKind: "court",
    group: "featured",
    branch: "criminal",
    source:
      "Read from the PDF served by sci.gov.in (listed under Judgments on the court's homepage) on 4 October 2026. Holding written from the judgment itself, not from the court's summary.",
    reviewedOn: "2026-10-04",
    verified: false,
  },
  {
    court: "Supreme Court of India",
    decidedOn: "2026-09-30",
    title: "Orris Infrastructure Private Limited v. Rakesh Kumar Gupta & Ors. (the court's homepage lists the lead appeal as Greenopolis Welfare Confederation v. Rakesh Kumar Gupta)",
    caseNumber: "Civil Appeal Nos. 6797-6801 of 2023 with C.A. Nos. 6792-6796 and 6802-6806 of 2023; 2026 INSC 1070; P. Sri Narasimha and Alok Aradhe JJ.",
    holding:
      "Under the Insolvency and Bankruptcy Code, if the facts that justified starting insolvency proceedings (sections 7, 9 or 10) were fraudulent and collusive, the adjudicating authority can recall the admission. Once admitted, the proceedings no longer belong to the original applicant, who cannot withdraw. The authority may bar that applicant and may decide to continue the process for the sake of other stakeholders, after hearing the resolution professional, the creditors' committee and others (para 49). The matter went back to the authority to decide (para 50).",
    url: "https://www.sci.gov.in/view-pdf/?diary_no=362522023&type=j&order_date=2026-09-30&from=latest_judgements_order",
    linkKind: "court",
    group: "featured",
    branch: "civil",
    source:
      "Read from the PDF served by sci.gov.in (listed under Judgments on the court's homepage) on 4 October 2026. Holding written from the judgment itself, not from the court's summary.",
    reviewedOn: "2026-10-04",
    verified: false,
  },
  {
    court: "Supreme Court of India",
    decidedOn: "2026-09-30",
    title: "M/s Awadhesh Singh Gautam v. State of Chhattisgarh & Ors.",
    caseNumber: "Civil Appeals arising out of SLP (C) Nos. 10464, 12766 and 12346 of 2026 (listed by the court as C.A. No. 13299/2026); 2026 INSC 1072 (non-reportable); P. Sri Narasimha and Alok Aradhe JJ.",
    holding:
      "A state road-development agency could not recover alleged overpayment on earlier contracts by appropriating money due under three separate later contracts. Neither the contract nor any law allowed it, and the question turned on the contract's terms (para 27). The recovery order was quashed and Rs 84,17,003 with 6% interest was ordered to be released. The State can still pursue the earlier dues in proper proceedings (paras 28-29).",
    url: "https://www.sci.gov.in/view-pdf/?diary_no=130912026&type=j&order_date=2026-09-30&from=latest_judgements_order",
    linkKind: "court",
    group: "featured",
    branch: "civil",
    source:
      "Read from the PDF served by sci.gov.in (listed under Judgments on the court's homepage) on 4 October 2026. Holding written from the judgment itself, not from the court's summary.",
    reviewedOn: "2026-10-04",
    verified: false,
  },
  {
    court: "Supreme Court of India",
    decidedOn: "2026-09-30",
    title: "Sterling Holiday Resorts Limited v. M/s P.M. Associates & Ors.",
    caseNumber: "Civil Appeal Nos. 10077-10078 of 2014 with C.A. Nos. 10246-10247 of 2014 and connected matters; 2026 INSC 1071 (non-reportable); P. Sri Narasimha and Alok Aradhe JJ.",
    holding:
      "A sale under the SARFAESI Act was held illegal. Rules 8 and 9 of the enforcement rules are mandatory, and the thirty days' notice gives the borrower a real last chance to redeem (para 30). A bid was received while the appellate tribunal's restraint was in force, and the sale came before thirty days had run once the restraint period is excluded (para 31). The sale was set aside and the purchaser's claim failed (paras 35-36).",
    url: "https://www.sci.gov.in/view-pdf/?diary_no=276332013&type=j&order_date=2026-09-30&from=latest_judgements_order",
    linkKind: "court",
    group: "featured",
    branch: "civil",
    source:
      "Read from the PDF served by sci.gov.in (listed under Judgments on the court's homepage) on 4 October 2026. Holding written from the judgment itself, not from the court's summary.",
    reviewedOn: "2026-10-04",
    verified: false,
  },
];

/**
 * Before launch, flip this to true so only entries with `verified: true`
 * are shown. While it is false, unverified entries carry the
 * "Draft: not yet checked" badge instead.
 */
export const HIDE_UNVERIFIED = true;

/** Entries the Rulings page may show right now. */
export function visibleRulings(list: RulingEntry[]): RulingEntry[] {
  return HIDE_UNVERIFIED ? list.filter((r) => r.verified) : list;
}

/** Newest `reviewedOn` across a list, or null. */
export function lastReviewed(list: RulingEntry[]): string | null {
  const dates = list.map((r) => r.reviewedOn).filter(Boolean).sort();
  return dates.length ? dates[dates.length - 1] : null;
}
