/**
 * Background judgments on which code applies to an offence committed before
 * 1 July 2024. Used as the Overview fallback when the archive route can't be
 * reached, and shown as the "Background" group on the Rulings page (next pass).
 *
 * Every field below was read from the judgment PDF itself on `reviewedOn`
 * (copies hosted by LiveLaw, not the courts' own sites, so linkKind is
 * "archive"). Nothing was filled from memory. All entries are still
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
  linkKind: "court" | "archive";
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
    linkKind: "archive",
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
    linkKind: "archive",
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
    linkKind: "archive",
    branch: "criminal",
    topic: "ipc-bns",
    source:
      "Read from the judgment PDF (LiveLaw copy). Printed: reserved 22.10.2024, pronounced 25.10.2024. No neutral citation is printed on the copy read.",
    reviewedOn: "2026-10-04",
    verified: false,
  },
];
