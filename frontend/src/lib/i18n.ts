import type { Lang } from "./prefs";

export type Dictionary = {
  about: string;
  login: string;
  signUp: string;
  heroHeadline: string;
  heroSupport: string;
  heroCta: string;
  offenseDate: string;
  cutoffLabel: string;
  pickOffenseDate: string;
  applies: string;
  noteIpc: string;
  noteBns: string;
  noteEmpty: string;
  gateFine: string;
  trustAria: string;
  trustCard1Title: string;
  trustCard1Body: string;
  trustCard2Title: string;
  trustCard2Body: string;
  trustCard3Title: string;
  trustCard3Body: string;
  trustEvalLink: string;
  compareHeading: string;
  compareLede: string;
  compareCapability: string;
  colStatic: string;
  colDense: string;
  colLawShift: string;
  rowArt20: string;
  rowBifurcation: string;
  rowTrace: string;
  rowPlain: string;
  rowHallucination: string;
  cellManual: string;
  cellModel: string;
  cellHardGate: string;
  cellSingleHit: string;
  cellSilentTop: string;
  cellScoreGap: string;
  cellTableOnly: string;
  cellOpaque: string;
  cellCascade: string;
  cellRawStatute: string;
  cellUnconstrained: string;
  cellConstrainedIrac: string;
  cellLowNoGen: string;
  cellHigh: string;
  cellZeroFab: string;
  chatHeading: string;
  chatLede: string;
  mapSection: string;
  thinkDeeper: string;
  legalResearch: string;
  analyzeDocument: string;
  analyzeHint: string;
  emptyTitle: string;
  emptyBody: string;
  caseQuestion: string;
  composerPlaceholder: string;
  send: string;
  running: string;
  freeOne: string;
  freeMany: (n: number) => string;
  mapped: string;
  verifierNote: string;
  sourcesHeading: (n: number) => string;
  showSourceText: string;
  hideSourceText: string;
  verifyOk: string;
  worthDoubleChecking: string;
  clarifyFallback: string;
  clarifyFallbackFacts: string;
  clarifyFallbackMismatch: string;
  clarifyFallbackDescribeFacts: string;
  sectionLookupNoteFallback: string;
  sectionLookupExhaustedNote: string;
  sectionLookupNoEquivalent: string;
  sectionLookupMissing: (code: string, section: string) => string;
  sectionMissingSearchNote: (code: string, section: string) => string;
  sectionLookupMapping: (
    otherCodeName: string,
    phrase: string,
    label: string,
    heading: string,
  ) => string;
  mappingPhraseSection: string;
  mappingPhrasePartial: string;
  mappingPhraseMerged: string;
  offenseDateUsedLine: (date: string, codeName: string) => string;
  offenseDateFromEarlier: string;
  offenseDateFromDocument: string;
  offenseDateConfirmed: string;
  exceptionProvisoNotice: string;
  scopeLine: string;
  /** Code-written Conclusion; code/section/heading stay as stored. */
  fixedConclusion: (code: string, section: string, heading: string) => string;
  langSwitchNote: (langName: string) => string;
  langNameEn: string;
  langNameHi: string;
  langNameMr: string;
  codeNameIpc: string;
  codeNameBns: string;
  bifurcationEscapeOption: string;
  dateLockNote: (date: string) => string;
  bifurcationDateConflictFallback: (
    earlierDate: string,
    earlierCode: string,
    laterDate: string,
    laterCode: string,
  ) => string;
  machineTranslatedNote: string;
  numberGuardFallbackNote: string;
  bifurcationPrompt: (sections: string) => string;
  bifurcationMismatchFallback: (sections: string) => string;
  failureFallback: string;
  unexpected: string;
  apiError: string;
  translationFallbackNote: string;
  howHeading: string;
  howLede: string;
  stepExtract: string;
  stepExtractPhrase: string;
  stepGate: string;
  stepGatePhrase: string;
  stepRetrieve: string;
  stepRetrievePhrase: string;
  stepSynthesize: string;
  stepSynthesizePhrase: string;
  faqHeading: string;
  faqQ1: string;
  faqA1: string;
  faqQ2: string;
  faqA2: string;
  faqQ3: string;
  faqA3: string;
  faqQ4: string;
  faqA4: string;
  footerMeta: string;
  footerDisclaimer: string;
  you: string;
  assistant: string;
  issue: string;
  rule: string;
  application: string;
  generatedNote: string;
  conclusion: string;
};

const en: Dictionary = {
  about: "About",
  login: "Login",
  signUp: "Sign Up",
  heroHeadline:
    "Know which law applies — IPC or BNS — grounded in the actual statutory text, not a guess.",
  heroSupport: "Built for India's 2024 criminal law transition.",
  heroCta: "Open the workspace",
  offenseDate: "Offense date",
  cutoffLabel: "Cutoff:",
  pickOffenseDate: "Pick an offense date",
  applies: "Applies",
  noteIpc: "Before the cutoff — Indian Penal Code governs.",
  noteBns: "On or after the cutoff — Bharatiya Nyaya Sanhita governs.",
  noteEmpty: "Enter a date to see the gate.",
  gateFine: "Client-side replica of Stage 2's deterministic comparison — not a model guess.",
  trustAria: "Why trust LawShift",
  trustCard1Title: "Routes to the correct law, every time",
  trustCard1Body:
    "A hard rule based on the offence date decides IPC or BNS. Not an AI guess.",
  trustCard2Title: "Shows you the real statutory text",
  trustCard2Body:
    "Every answer is built from the actual section you'd find in the Bare Act, not a summary.",
  trustCard3Title: "Tells you when it's not sure",
  trustCard3Body:
    "When more than one section could apply, LawShift asks you to choose instead of silently picking one.",
  trustEvalLink: "See the full evaluation results →",
  compareHeading: "Why not a lookup table or a plain RAG chat?",
  compareLede:
    "The same comparison drawn in the project paper: what each approach can and cannot guarantee for India's code transition.",
  compareCapability: "Capability",
  colStatic: "Static lookup",
  colDense: "Dense RAG",
  colLawShift: "LawShift",
  rowArt20: "Art. 20(1) guarantee",
  rowBifurcation: "Bifurcation handling",
  rowTrace: "Retrieval traceability",
  rowPlain: "Plain-language output",
  rowHallucination: "Hallucination risk",
  cellManual: "Manual / brittle",
  cellModel: "Model-dependent",
  cellHardGate: "Hard date gate",
  cellSingleHit: "Single hit or miss",
  cellSilentTop: "Silent top-1",
  cellScoreGap: "Score-gap prompt",
  cellTableOnly: "Table only",
  cellOpaque: "Opaque scores",
  cellCascade: "Cascade + pipeline",
  cellRawStatute: "Raw statute",
  cellUnconstrained: "Unconstrained",
  cellConstrainedIrac: "Constrained IRAC",
  cellLowNoGen: "Low (no generation)",
  cellHigh: "High",
  cellZeroFab: "0 / 40 fabricated",
  chatHeading: "Ask a case question",
  chatLede: "The live workspace — same Stages 1–4 pipeline as the paper evaluation.",
  mapSection: "Map a Section",
  thinkDeeper: "Think Deeper",
  legalResearch: "Legal Research",
  analyzeDocument: "Analyze Document",
  analyzeHint: "Upload a PDF from the document endpoint, or paste the case facts here.",
  emptyTitle: "Start with an example, or write your own",
  emptyBody: "Give the facts and the date the offence happened. The answer will show the section it came from.",
  caseQuestion: "Case question",
  composerPlaceholder: "Describe the facts and the date…",
  send: "Send",
  running: "Running…",
  freeOne: "1 question left in this visit",
  freeMany: (n) => `${n} questions left in this visit`,
  mapped: "Mapped",
  verifierNote: "Verifier note",
  sourcesHeading: (n) => `Sources (${n})`,
  showSourceText: "Show statute text",
  hideSourceText: "Hide statute text",
  verifyOk: "No inconsistency detected",
  worthDoubleChecking: "Worth double-checking",
  clarifyFallback: "I need a clearer offense date.",
  clarifyFallbackFacts:
    "I have the date. Describe what happened (who did what, and to whom) so I can find the section.",
  clarifyFallbackMismatch:
    // Agent draft — needs native review
    "That section belongs to a different code than the one that applies on this date. No equivalent is recorded in our mapping table. Describe what happened so I can find the section.",
  clarifyFallbackDescribeFacts:
    // Agent draft — needs native review
    "Describe what happened (who did what, and to whom) and I will search again.",
  sectionLookupNoteFallback:
    // Agent draft — needs native review
    "You gave a section but no facts, so no analysis was written. Describe what happened to get one.",
  sectionLookupExhaustedNote:
    // Agent draft — needs native review
    "I could not narrow this down further. Open a section to read it, or add more detail.",
  sectionLookupNoEquivalent:
    // Agent draft — needs native review
    "No equivalent is recorded in our mapping table",
  sectionLookupMissing: (code, section) =>
    // Agent draft — needs native review
    `${code} ${section} is not in the statute text we hold.`,
  sectionMissingSearchNote: (code, section) =>
    // Agent draft — needs native review
    `${code} ${section} is not in the statute text we hold; searching on your facts instead.`,
  sectionLookupMapping: (otherCodeName, phrase, label, heading) => {
    // Agent draft — needs native review
    const suffix = heading ? ` (${heading})` : "";
    return `In ${otherCodeName}, ${phrase} ${label}${suffix}.`;
  },
  mappingPhraseSection: "the corresponding section is",
  mappingPhrasePartial: "partly matches",
  mappingPhraseMerged: "merged into",
  offenseDateUsedLine: (date, codeName) =>
    `Offence date used: ${date} (${codeName})`,
  offenseDateFromEarlier: "(from your earlier message)",
  offenseDateFromDocument: "(read from your document)",
  offenseDateConfirmed: "(confirmed by you)",
  exceptionProvisoNotice:
    "This section has an Exception, Explanation or Proviso that may change the result. Read the full text under Sources.",
  scopeLine:
    "This shows what the section says. Whether it applies to your facts is for a court to decide.",
  fixedConclusion: (code, section, heading) => {
    const head = (heading || "").trim();
    return head
      ? `On the facts described, this appears to fall within ${code} ${section} (${head}).`
      : `On the facts described, this appears to fall within ${code} ${section}.`;
  },
  langSwitchNote: (langName) =>
    `Answers already on screen stay in the language they were written in. New answers use ${langName}.`,
  langNameEn: "English",
  langNameHi: "Hindi",
  langNameMr: "Marathi",
  codeNameIpc: "the Indian Penal Code",
  codeNameBns: "the Bharatiya Nyaya Sanhita",
  bifurcationEscapeOption:
    // Agent draft — needs native review
    "None of these. I will describe what happened",
  dateLockNote: (date) =>
    // Agent draft — needs native review
    `Using the offence date you gave earlier: ${date}.`,
  bifurcationDateConflictFallback: (earlierDate, earlierCode, laterDate, laterCode) =>
    // Agent draft — needs native review
    `Earlier you gave ${earlierDate} (${earlierCode}). This message says ${laterDate} (${laterCode}). Which is the date of the offence?`,
  machineTranslatedNote:
    "Machine-translated after the legal analysis was done. Check the English if it matters.",
  numberGuardFallbackNote:
    "Part of this answer is shown in English because the translation changed a number.",
  bifurcationPrompt: (sections) =>
    `Several statutory sections look equally plausible for this query. Which one should I analyse: ${sections}?`,
  bifurcationMismatchFallback: (sections) =>
    // Agent draft — needs native review
    `You named a section from a code that is not in force on this offence date. In our mapping table the matching section(s) of the code that does apply are: ${sections}. Which should I analyse?`,
  failureFallback: "Could not complete this query.",
  unexpected: "Unexpected response from the pipeline.",
  apiError:
    "Could not reach the LawShift API. Start the FastAPI backend on port 8000, then try again.",
  translationFallbackNote:
    "Machine-translated with a fallback model. Verify against the English text.",
  howHeading: "How it works",
  howLede: "Four stages, same visual language as the architecture diagram in the paper.",
  stepExtract: "Extract",
  stepExtractPhrase: "Offense date from the facts",
  stepGate: "Gate",
  stepGatePhrase: "Hard IPC / BNS cutoff",
  stepRetrieve: "Retrieve",
  stepRetrievePhrase: "Act-aware cascade search",
  stepSynthesize: "Synthesize",
  stepSynthesizePhrase: "Grounded IRAC + verify",
  faqHeading: "FAQ",
  faqQ1: "Is this legal advice?",
  faqA1:
    "No. LawShift is an informational research tool that maps fact patterns to statutory text under India's 2024 criminal-law transition. It does not create an attorney–client relationship. For advice on a real matter, consult a qualified advocate.",
  faqQ2: "What languages does this support?",
  faqA2:
    "Queries run in English. Finished IRAC answers can be translated to Hindi (hi) or Marathi (mr) via the language toggle — a post-hoc step that never changes routing, retrieval, or verification. Use the EN / HI / MR control in the header.",
  faqQ3: "Is my data stored?",
  faqA3:
    "Conversation state used for date locking and bifurcation resolution is held in the running API process for the session. There is no long-term document warehouse in the current deployment. Do not paste privileged client files you are not authorized to process.",
  faqQ4: "How accurate is this?",
  faqA4:
    "Stage 2 routing is 100% accurate by construction against the 1 July 2024 cutoff. Held-out retrieval Recall@5 is 0.841 on the selected model test set. Across 40 constrained generations, zero fabricated citations were found; logical consistency failures still occur and are surfaced by the Rule-only verifier when possible.",
  footerMeta:
    "Built on GSMS-B, nandhakumarg IPC↔BNS mapping, GovIntel, nyaya-eval-v0, and AI4Bharat IndicTrans2. Selected retrieval model: fine-tuned bge-small (e8).",
  footerDisclaimer: "LawShift is an informational tool, not legal advice.",
  you: "You",
  assistant: "LawShift",
  issue: "Issue",
  rule: "Rule",
  application: "Application",
  generatedNote: "Generated text. It can say more than you told it. The statute text is under Sources.",
  conclusion: "Conclusion",
};

const hi: Dictionary = {
  about: "परिचय",
  login: "लॉगिन",
  signUp: "साइन अप",
  heroHeadline:
    "जानें कौन सा कानून लागू होता है — IPC या BNS — अनुमान नहीं, वास्तविक वैधानिक पाठ पर आधारित।",
  heroSupport: "भारत के 2024 आपराधिक कानून परिवर्तन के लिए निर्मित।",
  heroCta: "कार्यक्षेत्र खोलें",
  offenseDate: "अपराध की तिथि",
  cutoffLabel: "कटऑफ:",
  pickOffenseDate: "अपराध की तिथि चुनें",
  applies: "लागू",
  noteIpc: "कटऑफ से पहले — भारतीय दंड संहिता (IPC) लागू होती है।",
  noteBns: "कटऑफ पर या उसके बाद — भारतीय न्याय संहिता (BNS) लागू होती है।",
  noteEmpty: "गेट देखने के लिए तिथि दर्ज करें।",
  gateFine: "स्टेज 2 की नियतात्मक तुलना का क्लाइंट-साइड अनुकरण — मॉडल का अनुमान नहीं।",
  trustAria: "LawShift पर भरोसा क्यों",
  trustCard1Title: "हर बार सही कानून तक पहुँचाता है",
  trustCard1Body:
    "अपराध की तिथि पर आधारित कठोर नियम IPC या BNS तय करता है। यह AI का अनुमान नहीं है।",
  trustCard2Title: "वास्तविक वैधानिक पाठ दिखाता है",
  trustCard2Body:
    "हर उत्तर Bare Act में मिले वास्तविक धारा से बना है, सारांश से नहीं।",
  trustCard3Title: "जब अनिश्चित हो, बताता है",
  trustCard3Body:
    "जब एक से अधिक धारा लागू हो सकती हो, LawShift चुपचाप एक न चुनकर आपसे पूछता है।",
  trustEvalLink: "पूर्ण मूल्यांकन परिणाम देखें →",
  compareHeading: "लुकअप तालिका या साधारण RAG चैट क्यों नहीं?",
  compareLede:
    "पेपर में दर्शाया गया वही तुलनात्मक विश्लेषण: भारत के कोड परिवर्तन के लिए प्रत्येक दृष्टिकोण क्या गारंटी दे सकता है और क्या नहीं।",
  compareCapability: "क्षमता",
  colStatic: "स्थिर लुकअप",
  colDense: "Dense RAG",
  colLawShift: "LawShift",
  rowArt20: "अनुच्छेद 20(1) की गारंटी",
  rowBifurcation: "द्विभाजन प्रबंधन",
  rowTrace: "रिट्रीवल ट्रेसेबिलिटी",
  rowPlain: "सरल भाषा आउटपुट",
  rowHallucination: "भ्रांति / हेलुसिनेशन जोखिम",
  cellManual: "मैनुअल / कमज़ोर",
  cellModel: "मॉडल-निर्भर",
  cellHardGate: "कठोर तिथि गेट",
  cellSingleHit: "एकल हिट या चूक",
  cellSilentTop: "मौन top-1",
  cellScoreGap: "स्कोर-गैप प्रॉम्प्ट",
  cellTableOnly: "केवल तालिका",
  cellOpaque: "अस्पष्ट स्कोर",
  cellCascade: "कैस्केड + पाइपलाइन",
  cellRawStatute: "कच्चा क़ानून",
  cellUnconstrained: "अनियंत्रित",
  cellConstrainedIrac: "बाध्य IRAC",
  cellLowNoGen: "कम (कोई जनरेशन नहीं)",
  cellHigh: "उच्च",
  cellZeroFab: "0 / 40 गढ़े गए",
  chatHeading: "केस प्रश्न पूछें",
  chatLede: "लाइव कार्यक्षेत्र — पेपर मूल्यांकन जैसी ही स्टेज 1–4 पाइपलाइन।",
  mapSection: "धारा मैप करें",
  thinkDeeper: "गहरा सोचें",
  legalResearch: "कानूनी शोध",
  analyzeDocument: "दस्तावेज़ विश्लेषण",
  analyzeHint: "दस्तावेज़ एंडपॉइंट से PDF अपलोड करें, या केस तथ्य यहाँ पेस्ट करें।",
  emptyTitle: "उदाहरण से शुरू करें, या अपना लिखें",
  emptyBody: "उदाहरण आज़माएँ, या अपराध की तिथि सहित तथ्य लिखें।",
  caseQuestion: "केस प्रश्न",
  composerPlaceholder: "तथ्य और तिथि लिखें…",
  send: "भेजें",
  running: "चल रहा है…",
  freeOne: "इस विज़िट में 1 प्रश्न शेष",
  freeMany: (n) => `इस विज़िट में ${n} प्रश्न शेष`,
  mapped: "मैप किया गया",
  verifierNote: "सत्यापनकर्ता नोट",
  sourcesHeading: (n) => `स्रोत (${n})`,
  showSourceText: "वैधानिक पाठ दिखाएँ",
  hideSourceText: "वैधानिक पाठ छिपाएँ",
  verifyOk: "कोई असंगति नहीं मिली",
  worthDoubleChecking: "दोबारा जाँचने योग्य",
  clarifyFallback: "मुझे स्पष्ट अपराध तिथि चाहिए।",
  clarifyFallbackFacts:
    "तिथि मिल गई है। क्या हुआ था लिखें (किसने क्या किया, और किसके साथ), ताकि मैं धारा ढूँढ सकूँ।",
  clarifyFallbackMismatch:
    // Agent draft — needs native review
    "यह धारा उस संहिता की नहीं है जो इस तिथि पर लागू होती है। हमारी मैपिंग तालिका में कोई समकक्ष दर्ज नहीं है। क्या हुआ था लिखें ताकि मैं धारा ढूँढ सकूँ।",
  clarifyFallbackDescribeFacts:
    // Agent draft — needs native review
    "क्या हुआ था लिखें (किसने क्या किया, और किसके साथ) — मैं फिर से खोजूँगा।",
  sectionLookupNoteFallback:
    // Agent draft — needs native review
    "आपने धारा दी है लेकिन तथ्य नहीं, इसलिए विश्लेषण नहीं लिखा गया। विश्लेषण के लिए क्या हुआ था बताएँ।",
  sectionLookupExhaustedNote:
    // Agent draft — needs native review
    "मैं इसे और सीमित नहीं कर सका। धारा पढ़ने के लिए खोलें, या और विवरण जोड़ें।",
  sectionLookupNoEquivalent:
    // Agent draft — needs native review
    "हमारी मैपिंग तालिका में कोई समकक्ष दर्ज नहीं है",
  sectionLookupMissing: (code, section) =>
    // Agent draft — needs native review
    `${code} ${section} हमारे पास रखे वैधानिक पाठ में नहीं है।`,
  sectionMissingSearchNote: (code, section) =>
    // Agent draft — needs native review
    `${code} ${section} हमारे पास रखे वैधानिक पाठ में नहीं है; आपके तथ्यों पर खोज जारी है।`,
  sectionLookupMapping: (otherCodeName, phrase, label, heading) => {
    // Agent draft — needs native review
    const suffix = heading ? ` (${heading})` : "";
    return `${otherCodeName} में, ${phrase} ${label}${suffix}।`;
  },
  mappingPhraseSection: "समकक्ष धारा है",
  mappingPhrasePartial: "आंशिक रूप से मेल खाती है",
  mappingPhraseMerged: "विलीन है",
  offenseDateUsedLine: (date, codeName) =>
    // Agent draft — needs native review
    `उपयोग की गई अपराध तिथि: ${date} (${codeName})`,
  offenseDateFromEarlier:
    // Agent draft — needs native review
    "(आपके पहले संदेश से)",
  offenseDateFromDocument:
    // Agent draft — needs native review
    "(आपके दस्तावेज़ से पढ़ी गई)",
  offenseDateConfirmed:
    // Agent draft — needs native review
    "(आपके द्वारा पुष्टि की गई)",
  exceptionProvisoNotice:
    // Agent draft — needs native review
    "इस धारा में Exception, Explanation या Proviso हो सकता है जो परिणाम बदल सके। स्रोतों में पूरा पाठ पढ़ें।",
  scopeLine:
    // Agent draft — needs native review
    "यह दिखाता है कि धारा क्या कहती है। यह आपके तथ्यों पर लागू होती है या नहीं, न्यायालय तय करेगा।",
  fixedConclusion: (code, section, heading) => {
    // Agent draft — needs native review
    const head = (heading || "").trim();
    return head
      ? `वर्णित तथ्यों के आधार पर, यह ${code} ${section} (${head}) के अंतर्गत आता प्रतीत होता है।`
      : `वर्णित तथ्यों के आधार पर, यह ${code} ${section} के अंतर्गत आता प्रतीत होता है।`;
  },
  langSwitchNote: (langName) =>
    // Agent draft — needs native review
    `स्क्रीन पर पहले से लिखे उत्तर जिस भाषा में हैं उसी में रहेंगे। नए उत्तर ${langName} में होंगे।`,
  langNameEn: "English",
  langNameHi: "हिंदी",
  langNameMr: "मराठी",
  codeNameIpc: "भारतीय दंड संहिता",
  codeNameBns: "भारतीय न्याय संहिता",
  bifurcationEscapeOption:
    // Agent draft — needs native review
    "इनमें से कोई नहीं। मैं बताऊँगा कि क्या हुआ।",
  dateLockNote: (date) =>
    // Agent draft — needs native review
    `आपकी पहले दी गई अपराध तिथि उपयोग हो रही है: ${date}।`,
  bifurcationDateConflictFallback: (earlierDate, earlierCode, laterDate, laterCode) =>
    // Agent draft — needs native review
    `पहले आपने ${earlierDate} (${earlierCode}) दी थी। इस संदेश में ${laterDate} (${laterCode}) है। अपराध की तिथि कौन-सी है?`,
  machineTranslatedNote:
    "कानूनी विश्लेषण पूरा होने के बाद हिंदी में मशीन-अनुवाद किया गया। ज़रूरी हो तो अंग्रेज़ी पाठ देखें।",
  numberGuardFallbackNote:
    // Agent draft — needs native review
    "इस उत्तर का कुछ भाग अंग्रेज़ी में दिखाया गया है क्योंकि अनुवाद ने कोई संख्या बदल दी।",
  bifurcationPrompt: (sections) =>
    `इस प्रश्न के लिए कई वैधानिक धाराएँ लगभग समान रूप से उपयुक्त लगती हैं। मैं किसका विश्लेषण करूँ: ${sections}?`,
  bifurcationMismatchFallback: (sections) =>
    // Agent draft — needs native review
    `आपने ऐसी संहिता की धारा लिखी है जो इस अपराध तिथि पर लागू नहीं होती। मैपिंग तालिका में लागू संहिता की समकक्ष धाराएँ हैं: ${sections}। मैं किसका विश्लेषण करूँ?`,
  failureFallback: "यह क्वेरी पूरी नहीं हो सकी।",
  unexpected: "पाइपलाइन से अप्रत्याशित प्रतिक्रिया।",
  apiError:
    "LawShift API तक पहुँच नहीं हो सकी। पोर्ट 8000 पर FastAPI बैकएंड चालू करें, फिर पुनः प्रयास करें।",
  translationFallbackNote:
    "फ़ॉलबैक मॉडल से मशीन-अनुवादित। अंग्रेज़ी पाठ से सत्यापित करें।",
  howHeading: "यह कैसे काम करता है",
  howLede: "चार चरण — पेपर के आर्किटेक्चर आरेख जैसी दृश्य भाषा।",
  stepExtract: "निष्कर्षण",
  stepExtractPhrase: "तथ्यों से अपराध तिथि",
  stepGate: "गेट",
  stepGatePhrase: "कठोर IPC / BNS कटऑफ",
  stepRetrieve: "रिट्रीव",
  stepRetrievePhrase: "एक्ट-अवेयर कैस्केड खोज",
  stepSynthesize: "संश्लेषण",
  stepSynthesizePhrase: "आधारित IRAC + सत्यापन",
  faqHeading: "अक्सर पूछे जाने वाले प्रश्न",
  faqQ1: "क्या यह कानूनी सलाह है?",
  faqA1:
    "नहीं। LawShift एक सूचनात्मक शोध उपकरण है जो भारत के 2024 आपराधिक-कानून परिवर्तन के अंतर्गत तथ्य-पैटर्न को वैधानिक पाठ से जोड़ता है। यह वकील–मुवक्किल संबंध नहीं बनाता। वास्तविक मामले में योग्य अधिवक्ता से सलाह लें।",
  faqQ2: "यह कौन-सी भाषाएँ समर्थन करता है?",
  faqA2:
    "क्वेरी अंग्रेज़ी में चलती हैं। पूर्ण IRAC उत्तर भाषा टॉगल से हिंदी (hi) या मराठी (mr) में अनुवादित हो सकते हैं — यह केवल पोस्ट-हॉक चरण है; रूटिंग, रिट्रीवल या सत्यापन नहीं बदलता। हेडर में EN / HI / MR नियंत्रण उपयोग करें।",
  faqQ3: "क्या मेरा डेटा संग्रहीत होता है?",
  faqA3:
    "तिथि लॉक और द्विभाजन समाधान के लिए वार्तालाप स्थिति सत्र भर API प्रक्रिया में रहती है। वर्तमान परिनियोजन में दीर्घकालिक दस्तावेज़ भंडार नहीं है। ऐसे विशेषाधिकार प्राप्त फ़ाइलें न चिपकाएँ जिनके प्रसंस्करण का अधिकार आपके पास नहीं है।",
  faqQ4: "यह कितना सटीक है?",
  faqA4:
    "स्टेज 2 रूटिंग 1 जुलाई 2024 कटऑफ के सापेक्ष संरचना द्वारा 100% सटीक है। चयनित मॉडल के held-out परीक्षण पर रिट्रीवल Recall@5 0.841 है। 40 बाध्य जनरेशन में शून्य गढ़े गए उद्धरण मिले; तार्किक-संगति विफलताएँ अलग श्रेणी हैं और संभव होने पर Rule-only सत्यापनकर्ता उन्हें दिखाता है।",
  footerMeta:
    "GSMS-B, nandhakumarg IPC↔BNS मैपिंग, GovIntel, nyaya-eval-v0, और AI4Bharat IndicTrans2 पर आधारित। चयनित रिट्रीवल मॉडल: fine-tuned bge-small (e8)।",
  footerDisclaimer: "LawShift एक सूचनात्मक उपकरण है, कानूनी सलाह नहीं।",
  you: "आप",
  assistant: "LawShift",
  issue: "मुद्दा",
  rule: "नियम",
  application: "अनुप्रयोग",
  generatedNote: "मॉडल द्वारा लिखा पाठ। यह आपके बताए से ज़्यादा कह सकता है। धारा का पाठ स्रोत में है।",
  conclusion: "निष्कर्ष",
};

const mr: Dictionary = {
  about: "परिचय",
  login: "लॉगिन",
  signUp: "साइन अप",
  heroHeadline:
    "कोणता कायदा लागू होतो ते जाणून घ्या — IPC की BNS — अंदाजाने नव्हे, प्रत्यक्ष वैधानिक मजकुरावर आधारित.",
  heroSupport: "भारताच्या २०२४ च्या फौजदारी कायदा बदलासाठी तयार केलेले.",
  heroCta: "कार्यक्षेत्र उघडा",
  offenseDate: "गुन्ह्याची तारीख",
  cutoffLabel: "कटऑफ:",
  pickOffenseDate: "गुन्ह्याची तारीख निवडा",
  applies: "लागू",
  noteIpc: "कटऑफपूर्वी — भारतीय दंड संहिता (IPC) लागू होते.",
  noteBns: "कटऑफवर किंवा नंतर — भारतीय न्याय संहिता (BNS) लागू होते.",
  noteEmpty: "गेट पाहण्यासाठी तारीख टाका.",
  gateFine: "स्टेज २ च्या निर्धारक तुलनेचे क्लायंट-साइड अनुकरण — मॉडेलचा अंदाज नाही.",
  trustAria: "LawShift वर विश्वास का करावा",
  trustCard1Title: "नेहमी योग्य कायद्याकडे नेतो",
  trustCard1Body:
    "अपराधाच्या तारखेवर आधारित कठोर नियम IPC किंवा BNS ठरवतो. हे AIचे अंदाज नाही.",
  trustCard2Title: "खरा वैधानिक मजकूर दाखवतो",
  trustCard2Body:
    "प्रत्येक उत्तर Bare Act मधील वास्तविक कलमावरून बनते, सारांशातून नाही.",
  trustCard3Title: "जेव्हा खात्री नसेल ते सांगतो",
  trustCard3Body:
    "एकाहून अधिक कलमे लागू होऊ शकतात तेव्हा LawShift शांतपणे एक निवडण्याऐवजी तुम्हाला विचारतो.",
  trustEvalLink: "पूर्ण मूल्यांकन निकाल पहा →",
  compareHeading: "लुकअप तक्ता किंवा साधा RAG चॅट का नाही?",
  compareLede:
    "पेपरमधील तोच तुलनात्मक आढावा: भारताच्या कोड बदलासाठी प्रत्येक पद्धत काय हमी देऊ शकते आणि काय नाही.",
  compareCapability: "क्षमता",
  colStatic: "स्थिर लुकअप",
  colDense: "Dense RAG",
  colLawShift: "LawShift",
  rowArt20: "अनुच्छेद २०(१) हमी",
  rowBifurcation: "द्विभाजन हाताळणी",
  rowTrace: "रिट्रीवल ट्रेसेबिलिटी",
  rowPlain: "साध्या भाषेतील आउटपुट",
  rowHallucination: "भ्रांती / हेलुसिनेशन जोखीम",
  cellManual: "मॅन्युअल / नाजूक",
  cellModel: "मॉडेल-अवलंबित",
  cellHardGate: "कठोर तारीख गेट",
  cellSingleHit: "एकल हिट किंवा चूक",
  cellSilentTop: "मौन top-1",
  cellScoreGap: "स्कोर-गॅप प्रॉम्प्ट",
  cellTableOnly: "फक्त तक्ता",
  cellOpaque: "अस्पष्ट स्कोअर",
  cellCascade: "कॅस्केड + पाइपलाइन",
  cellRawStatute: "कच्चा कायदा",
  cellUnconstrained: "अनियंत्रित",
  cellConstrainedIrac: "बंधित IRAC",
  cellLowNoGen: "कमी (जनरेशन नाही)",
  cellHigh: "जास्त",
  cellZeroFab: "० / ४० बनावट",
  chatHeading: "केस प्रश्न विचारा",
  chatLede: "लाइव्ह कार्यक्षेत्र — पेपर मूल्यांकनासारखीच स्टेज १–४ पाइपलाइन.",
  mapSection: "कलम मॅप करा",
  thinkDeeper: "खोलवर विचार करा",
  legalResearch: "कायदेशीर संशोधन",
  analyzeDocument: "दस्तऐवज विश्लेषण",
  analyzeHint: "दस्तऐवज एंडपॉइंटवरून PDF अपलोड करा, किंवा केस तथ्ये येथे पेस्ट करा.",
  emptyTitle: "उदाहरणाने सुरुवात करा, किंवा स्वतः लिहा",
  emptyBody: "उदाहरण वापरा, किंवा गुन्ह्याची तारीख सहित तथ्ये लिहा.",
  caseQuestion: "केस प्रश्न",
  composerPlaceholder: "तथ्ये आणि तारीख लिहा…",
  send: "पाठवा",
  running: "चालू आहे…",
  freeOne: "या भेटीत १ प्रश्न शिल्लक",
  freeMany: (n) => `या भेटीत ${n} प्रश्न शिल्लक`,
  mapped: "मॅप केले",
  verifierNote: "सत्यापन टीप",
  sourcesHeading: (n) => `स्रोत (${n})`,
  showSourceText: "वैधानिक मजकूर दाखवा",
  hideSourceText: "वैधानिक मजकूर लपवा",
  verifyOk: "कोणतीही विसंगती आढळली नाही",
  worthDoubleChecking: "पुन्हा तपासण्यासारखे",
  clarifyFallback: "मला स्पष्ट गुन्हा तारीख हवी आहे.",
  clarifyFallbackFacts:
    "तारीख मिळाली आहे. काय झाले ते लिहा (कोणी काय केले, आणि कोणाशी), जेणेकरून मी कलम शोधू शकेन.",
  clarifyFallbackMismatch:
    // Agent draft — needs native review
    "हे कलम त्या संहितेचे नाही जे या तारखेला लागू होते. आमच्या मॅपिंग तक्त्यात समकक्ष नोंद नाही. काय झाले ते लिहा जेणेकरून मी कलम शोधू शकेन.",
  clarifyFallbackDescribeFacts:
    // Agent draft — needs native review
    "काय झाले ते लिहा (कोणी काय केले, आणि कोणाशी) — मी पुन्हा शोधेन.",
  sectionLookupNoteFallback:
    // Agent draft — needs native review
    "तुम्ही कलम दिले आहे पण तथ्य नाहीत, म्हणून विश्लेषण लिहिले नाही. विश्लेषणासाठी काय झाले ते सांगा.",
  sectionLookupExhaustedNote:
    // Agent draft — needs native review
    "मी हे आणखी मर्यादित करू शकलो नाही. कलम वाचण्यासाठी उघाडा, किंवा अधिक तपशील जोडा.",
  sectionLookupNoEquivalent:
    // Agent draft — needs native review
    "आमच्या मॅपिंग तक्त्यात समकक्ष नोंद नाही",
  sectionLookupMissing: (code, section) =>
    // Agent draft — needs native review
    `${code} ${section} आमच्याकडे असलेल्या वैधानिक मजकुरात नाही.`,
  sectionMissingSearchNote: (code, section) =>
    // Agent draft — needs native review
    `${code} ${section} आमच्याकडे असलेल्या वैधानिक मजकुरात नाही; तुमच्या तथ्यांवर शोध सुरू आहे.`,
  sectionLookupMapping: (otherCodeName, phrase, label, heading) => {
    // Agent draft — needs native review
    const suffix = heading ? ` (${heading})` : "";
    return `${otherCodeName} मध्ये, ${phrase} ${label}${suffix}.`;
  },
  mappingPhraseSection: "समकक्ष कलम आहे",
  mappingPhrasePartial: "अंशतः जुळते",
  mappingPhraseMerged: "विलीन आहे",
  offenseDateUsedLine: (date, codeName) =>
    // Agent draft — needs native review
    `वापरलेली गुन्ह्याची तारीख: ${date} (${codeName})`,
  offenseDateFromEarlier:
    // Agent draft — needs native review
    "(तुमच्या आधीच्या संदेशातून)",
  offenseDateFromDocument:
    // Agent draft — needs native review
    "(तुमच्या दस्तऐवजातून वाचले)",
  offenseDateConfirmed:
    // Agent draft — needs native review
    "(तुम्ही पुष्टी केलेली)",
  exceptionProvisoNotice:
    // Agent draft — needs native review
    "या कलमात Exception, Explanation किंवा Proviso असू शकते जे निकाल बदलू शकते. स्रोतांखाली संपूर्ण मजकूर वाचा.",
  scopeLine:
    // Agent draft — needs native review
    "हे कलम काय म्हणते ते दाखवते. तुमच्या तथ्यांवर लागू होते की नाही हे न्यायालय ठरवेल.",
  fixedConclusion: (code, section, heading) => {
    // Agent draft — needs native review
    const head = (heading || "").trim();
    return head
      ? `वर्णन केलेल्या तथ्यांनुसार, हे ${code} ${section} (${head}) अंतर्गत येत असल्याचे दिसते.`
      : `वर्णन केलेल्या तथ्यांनुसार, हे ${code} ${section} अंतर्गत येत असल्याचे दिसते.`;
  },
  langSwitchNote: (langName) =>
    // Agent draft — needs native review
    `स्क्रीनवरील आधीचे उत्तरे ज्या भाषेत आहेत तशाच राहतील. नवीन उत्तरे ${langName} मध्ये असतील.`,
  langNameEn: "English",
  langNameHi: "हिंदी",
  langNameMr: "मराठी",
  codeNameIpc: "भारतीय दंड संहिता",
  codeNameBns: "भारतीय न्याय संहिता",
  bifurcationEscapeOption:
    // Agent draft — needs native review
    "यापैकी कोणतेही नाही. काय घडले ते मी सांगतो.",
  dateLockNote: (date) =>
    // Agent draft — needs native review
    `तुम्ही आधी दिलेली गुन्ह्याची तारीख वापरली जात आहे: ${date}.`,
  bifurcationDateConflictFallback: (earlierDate, earlierCode, laterDate, laterCode) =>
    // Agent draft — needs native review
    `आधी तुम्ही ${earlierDate} (${earlierCode}) दिली. या संदेशात ${laterDate} (${laterCode}) आहे. गुन्ह्याची तारीख कोणती?`,
  machineTranslatedNote:
    "कायदेशीर विश्लेषणानंतर मराठीत मशीन-भाषांतर केले आहे. महत्त्वाचे असल्यास इंग्रजी मजकूर पाहा.",
  numberGuardFallbackNote:
    // Agent draft — needs native review
    "या उत्तराचा काही भाग इंग्रजीत दाखवला आहे कारण भाषांतराने एखादी संख्या बदलली.",
  bifurcationPrompt: (sections) =>
    `या प्रश्नासाठी अनेक वैधानिक कलमे जवळपास सारखीच योग्य वाटतात. मी कोणत्याचे विश्लेषण करू: ${sections}?`,
  bifurcationMismatchFallback: (sections) =>
    // Agent draft — needs native review
    `तुम्ही अशा संहितेचे कलम लिहिले आहे जे या गुन्ह्याच्या तारखेला लागू नाही. मॅपिंग तक्त्यात लागू संहितेची समकक्ष कलमे आहेत: ${sections}. मी कोणत्याचे विश्लेषण करू?`,
  failureFallback: "ही क्वेरी पूर्ण होऊ शकली नाही.",
  unexpected: "पाइपलाइनकडून अनपेक्षित प्रतिसाद.",
  apiError:
    "LawShift API पर्यंत पोहोचता आले नाही. पोर्ट ८००० वर FastAPI बॅकएंड सुरू करा आणि पुन्हा प्रयत्न करा.",
  translationFallbackNote:
    "फॉलबॅक मॉडेलने मशीन-अनुवादित. इंग्रजी मजकुराशी पडताळा.",
  howHeading: "हे कसे काम करते",
  howLede: "चार टप्पे — पेपरच्या आर्किटेक्चर आकृतीसारखी दृश्य भाषा.",
  stepExtract: "काढणे",
  stepExtractPhrase: "तथ्यांमधून गुन्हा तारीख",
  stepGate: "गेट",
  stepGatePhrase: "कठोर IPC / BNS कटऑफ",
  stepRetrieve: "रिट्रीव्ह",
  stepRetrievePhrase: "अॅक्ट-अवेयर कॅस्केड शोध",
  stepSynthesize: "संश्लेषण",
  stepSynthesizePhrase: "आधारित IRAC + सत्यापन",
  faqHeading: "नेहमी विचारले जाणारे प्रश्न",
  faqQ1: "हे कायदेशीर सल्ला आहे का?",
  faqA1:
    "नाही. LawShift हे माहितीपर संशोधन साधन आहे जे भारताच्या २०२४ फौजदारी-कायदा बदलांतर्गत तथ्य-नमुन्यांना वैधानिक मजकुराशी जोडते. हे वकील–मुवक्किल संबंध निर्माण करत नाही. वास्तविक प्रकरणात पात्र अधिवक्त्यांचा सल्ला घ्या.",
  faqQ2: "कोणत्या भाषा समर्थित आहेत?",
  faqA2:
    "क्वेरी इंग्रजीत चालतात. पूर्ण IRAC उत्तरे भाषा टॉगलने हिंदी (hi) किंवा मराठी (mr) मध्ये अनुवादित होऊ शकतात — हे केवळ नंतरचे पाऊल आहे; रूटिंग, रिट्रीवल किंवा सत्यापन बदलत नाही. हेडरमधील EN / HI / MR नियंत्रण वापरा.",
  faqQ3: "माझा डेटा साठवला जातो का?",
  faqA3:
    "तारीख लॉक आणि द्विभाजन निराकरणासाठी संभाषण स्थिती सत्रात API प्रक्रियेत ठेवली जाते. सध्याच्या तैनातीत दीर्घकालीन दस्तऐवज भांडार नाही. ज्या विशेषाधिकारित फाइल्सवर प्रक्रिया करण्याचा अधिकार नाही त्या पेस्ट करू नका.",
  faqQ4: "हे किती अचूक आहे?",
  faqA4:
    "स्टेज २ रूटिंग १ जुलै २०२४ कटऑफच्या तुलनेत रचनेनुसार १००% अचूक आहे. निवडलेल्या मॉडेलच्या held-out चाचणीवर रिट्रीवल Recall@5 ०.८४१ आहे. ४० बंधित जनरेशनमध्ये शून्य बनावट उद्धरणे आढळली; तार्किक-सुसंगतता अपयश वेगळी श्रेणी आहेत आणि शक्य असल्यास Rule-only सत्यापनकर्ता ती दाखवतो.",
  footerMeta:
    "GSMS-B, nandhakumarg IPC↔BNS मॅपिंग, GovIntel, nyaya-eval-v0, आणि AI4Bharat IndicTrans2 वर आधारित. निवडलेले रिट्रीवल मॉडेल: fine-tuned bge-small (e8).",
  footerDisclaimer: "LawShift हे माहितीपर साधन आहे, कायदेशीर सल्ला नाही.",
  you: "तुम्ही",
  assistant: "LawShift",
  issue: "मुद्दा",
  rule: "नियम",
  application: "अनुप्रयोग",
  generatedNote: "मॉडेलने लिहिलेला मजकूर. तो तुम्ही सांगितल्यापेक्षा जास्त सांगू शकतो. कलमाचा मजकूर स्रोतांमध्ये आहे.",
  conclusion: "निष्कर्ष",
};

const DICTS: Record<Lang, Dictionary> = { en, hi, mr };

export function getDictionary(lang: Lang): Dictionary {
  return DICTS[lang] ?? en;
}
