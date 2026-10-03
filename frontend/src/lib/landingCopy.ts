import type { Lang } from "./prefs";

/** Static marketing copy for the landing page (EN / HI / MR).
 *  Separate from live IRAC translation via IndicTrans2. */
export type LandingCopy = {
  navHow: string;
  navEvidence: string;
  navAbout: string;
  answersIn: string;
  tryACase: string;

  heroTitle: string;
  heroLead: string;
  heroCta: string;
  heroChecks: string;
  audience: string;

  docketBefore: string;
  docketAfter: string;
  docketIpcName: string;
  docketBnsName: string;
  docketCaption: string;
  docketTry: string;
  case1Facts: string;
  case1ResultNote: string;
  case2Facts: string;
  case2ResultNote: string;
  case3Facts: string;
  case3ResultNote: string;
  compareTitle: string;
  compareLead: string;
  compareIpcSpan: string;
  compareBnsSpan: string;
  compareSwap: string;
  compareRow1: string;
  compareRow2: string;
  compareMapped: string;
  compareChanged: string;
  compareSource: string;

  chatTitle: string;
  chatLead: string;
  chatTip1: string;
  chatTip2: string;
  chatTip3: string;

  howTitle: string;
  howLead: string;
  step1Title: string;
  step1Who: string;
  step1Body: string;
  step2Title: string;
  step2Who: string;
  step2Body: string;
  step3Title: string;
  step3Who: string;
  step3Body: string;
  step4Title: string;
  step4Who: string;
  step4Body: string;

  checksTitle: string;
  checksLead: string;
  outcome1When: string;
  outcome1Then: string;
  outcome2When: string;
  outcome2Then: string;
  outcome3When: string;
  outcome3Then: string;
  outcome4When: string;
  outcome4Then: string;
  checkerTitle: string;
  checkerP1: string;
  checkerP2: string;

  evidenceTitle: string;
  evidenceLead: string;
  evidence1Asked: string;
  evidence1Result: string;
  evidence1Fine: string;
  evidence2Asked: string;
  evidence2Result: string;
  evidence2Fine: string;
  evidence3Asked: string;
  evidence3Result: string;
  evidence3Fine: string;
  evidenceColAsked: string;
  evidenceColFound: string;
  evidenceColFine: string;
  evidenceMoreBefore: string;
  evidenceMoreLink: string;

  limitsTitle: string;
  limit1Title: string;
  limit1Body: string;
  limit2Title: string;
  limit2Body: string;
  limit3Title: string;
  limit3Body: string;
  limit4Title: string;
  limit4Body: string;

  skipLink: string;
  evidence1Fig: string;
  evidence3Fig: string;
  waffleLabelA: string;
  waffleLabelB: string;
  waffleHit: string;
  waffleMiss: string;
  waffleFigA: string;
  waffleFigB: string;
  stripTitle: string;
  stripCaught: string;
  stripFalse: string;
  stripClear: string;
  footerDisclaimer: string;
  footerCredits: string;
};

const en: LandingCopy = {
  navHow: "How it works",
  navEvidence: "What we measured",
  navAbout: "Research notes",
  answersIn: "Answers in",
  tryACase: "Try a case",

  heroTitle: "The day it happened decides which law applies.",
  heroLead:
    "On 1 July 2024 the Bharatiya Nyaya Sanhita (BNS) replaced the Indian Penal Code (IPC). A person cannot be punished under a law that was not in force when they acted, so both codes stay in use. Describe a case and LawShift works out which one applies, then shows you the section as written.",
  heroCta: "Describe a case",
  heroChecks: "How answers are checked",
  audience:
    "For law students, junior advocates and journalists. A research aid: not legal advice, and not a substitute for a lawyer.",

  docketBefore: "Before the cutoff",
  docketAfter: "On or after",
  docketIpcName: "Indian Penal Code, 1860",
  docketBnsName: "Bharatiya Nyaya Sanhita, 2023",
  docketCaption:
    "Recorded from our own test runs. The date alone decides which side a case falls on.",
  docketTry: "Try this case",
  case1Facts: "A bookstore owner sells obscene magazines for the first time.",
  case1ResultNote: "Sale of obscene books",
  case2Facts:
    "A riot breaks out for a landowner's benefit and the agent fails to prevent it.",
  case2ResultNote:
    "Liability of owner, occupier, etc., of land where a riot takes place",
  case3Facts: "A person is found in possession of counterfeit currency notes.",
  case3ResultNote:
    "Three offences fit about equally well, so it asks which one you mean",
  compareTitle:
    "Same offence, two codes",
  compareLead:
    "The first case in the timeline at the top falls under IPC 292. Had it happened on or after 1 July 2024, it would fall under BNS 294. Here is how the two texts read.",
  compareIpcSpan:
    "In force until 30 June 2024",
  compareBnsSpan:
    "In force from 1 July 2024",
  compareSwap:
    "1 July 2024",
  compareRow1:
    "What counts as obscene",
  compareRow2:
    "Punishment on first conviction",
  compareMapped:
    "The mapping table records IPC 292 → BNS 294 as a direct, one-to-one match.",
  compareChanged:
    "Words that differ between the two texts are highlighted.",
  compareSource:
    "Quoted from the IPC–BNS mapping table (nandhakumarg/IPC_and_BNS_transformation). Ellipses mark words left out, and footnote markers are removed. It is a community-maintained dataset, so check anything that matters against the official text.",

  chatTitle: "Try it on a case",
  chatLead:
    "Say what happened and when. The date decides the law, so if you leave it out, LawShift asks.",
  chatTip1: "Write the date in full, like 15 March 2024.",
  chatTip2: "Describe the facts in plain words. You can name a section too.",
  chatTip3:
    "Open the source text under each answer and read it. That is the check that matters.",

  howTitle: "What happens to your question",
  howLead:
    "Four steps, always in this order. Only the last one writes anything with a language model.",
  step1Title: "Find the date",
  step1Who: "Fixed rules, no model",
  step1Body:
    "LawShift reads the offence date out of your description. If there is no date, or one that could be read two ways, such as 07-01-2024, it asks you instead of guessing.",
  step2Title: "Pick the code",
  step2Who: "A date comparison",
  step2Body:
    "Before 1 July 2024 the Indian Penal Code applies. On or after it, the Bharatiya Nyaya Sanhita. This is a single comparison written in code. Nothing later in the process can override it.",
  step3Title: "Find the section",
  step3Who: "Search, limited to that code",
  step3Body:
    "It searches only the code chosen in step two, so IPC 201 and BNS 201 can never be mixed up. When two or more sections score almost the same, it shows you each one and asks which you mean.",
  step4Title: "Write it up and check it",
  step4Who: "Language models",
  step4Body:
    "A small model writes Issue, Rule, Application and Conclusion using only the section it was handed. A second, larger model then checks that the conclusion follows from the rule, and raises a flag if it may not.",

  checksTitle: "When it is not sure, it says so",
  checksLead:
    "A confident wrong answer is the worst thing a legal tool can give you. LawShift is built to look unsure when it is.",
  outcome1When: "You leave out the date",
  outcome1Then:
    "It asks what date this happened, because it cannot tell which law applies without one.",
  outcome2When: "Several sections fit equally well",
  outcome2Then: "It lists them with their opening lines and waits for you to choose.",
  outcome3When: "The conclusion may not follow from the rule",
  outcome3Then:
    "A note reading “Worth double-checking” appears next to the answer, with the reason.",
  outcome4When: "Nothing matches, or writing fails",
  outcome4Then: "It says so. It does not produce a plausible answer to fill the gap.",
  checkerTitle: "How good is the checker?",
  checkerP1:
    "We read 40 answers by hand. Five had a conclusion that did not follow from the rule. The checker flagged all five, and flagged ten good answers as well. When we later re-ran those five cases live, it caught two of them.",
  checkerP2:
    "So it is a second opinion, not a verdict. It raises a flag next to the statute text and never hides or blocks an answer.",

  evidenceTitle: "What we measured, and the fine print",
  evidenceLead:
    "Each result below comes from a test run saved in the project. Each comes with what it does not show.",
  evidenceColAsked: "We asked",
  evidenceColFound: "What we found",
  evidenceColFine: "The fine print",
  evidence1Asked: "Does it pick the right code?",
  evidence1Result: "Yes, every time. The rule only compares a date with 1 July 2024.",
  evidence1Fine:
    "Across 460 test questions. Here “right” is defined by that same rule, so this shows the rule is applied consistently; it is not a check that every date was read correctly. Reading dates out of free text was correct on 30 of 30 real questions and 14 of 14 awkward ones we wrote ourselves.",
  evidence2Asked: "Does it find the right section?",
  evidence2Result:
    "In 84 of every 100 held-out questions, the right section was among the five it retrieved.",
  evidence2Fine:
    "These were questions in the style of a statute Q&A set. On a separate set of 85 plainly worded questions, the figure was about 66 in 100. The answer is written from its first pick, which is not always the right one. That is why the section’s own text sits under every answer.",
  evidence3Asked: "Does it invent law?",
  evidence3Result:
    "Not in the 40 answers we read by hand: no made-up sections, no quotations that were not in the source.",
  evidence3Fine:
    "Those 40 were written with the correct section supplied, so this tests the writing step, not the search. It is a small sample. In 5 of the 40, the conclusion still did not follow from the rule.",
  evidenceMoreBefore: "Metrics, datasets and how each was measured are on the",
  evidenceMoreLink: "research notes",

  limitsTitle: "Where it stops",
  limit1Title: "It is not legal advice",
  limit1Body:
    "LawShift helps you read the statute faster. It does not weigh evidence, case law or procedure, and it does not replace a lawyer.",
  limit2Title: "A case that straddles the cutoff gets one answer",
  limit2Body:
    "If something was done before 1 July 2024 and continued after, LawShift uses one date and returns one code. A detector for such cases exists as a prototype, tested on 9 examples. It is not in the product yet.",
  limit3Title: "Before the cutoff, only the IPC is searched",
  limit3Body:
    "The text of the old Code of Criminal Procedure and Evidence Act is not included.",
  limit4Title: "Hindi and Marathi are machine-translated",
  limit4Body:
    "Translation happens last, after the legal analysis, so it cannot change which section was chosen. It can still be imperfect. Check the English if it matters.",

  skipLink: "Skip to main content",
  evidence1Fig: "460 of 460",
  evidence3Fig: "0 of 40",
  waffleLabelA: "Statute-style questions",
  waffleLabelB: "Plainly worded questions",
  waffleHit: "Right section in the top five",
  waffleMiss: "Not in the top five",
  waffleFigA: "84 of 100",
  waffleFigB: "about 66 of 100",
  stripTitle: "The checker on 40 hand-read answers",
  stripCaught: "Conclusion did not follow, flagged (5)",
  stripFalse: "Answer was fine, flagged anyway (10)",
  stripClear: "Answer was fine, not flagged (25)",
  footerDisclaimer:
    "LawShift is an informational research tool. It is not legal advice and does not replace a lawyer. Check anything that matters against the official text of the BNS, BNSS, BSA and IPC.",
  footerCredits:
    "Built on statute text and question sets from GSMS-B, the IPC–BNS mapping by nandhakumarg, GovIntel and nyaya-eval-v0, with translation by AI4Bharat IndicTrans2.",
};

const hi: LandingCopy = {
  navHow: "यह कैसे काम करता है",
  navEvidence: "हमने क्या मापा",
  navAbout: "अनुसंधान नोट्स",
  answersIn: "उत्तर की भाषा",
  tryACase: "एक केस आज़माएँ",

  heroTitle: "जिस दिन घटना हुई, वही तय करता है कौन-सा कानून लागू होगा।",
  heroLead:
    "1 जुलाई 2024 को भारतीय न्याय संहिता (BNS) ने भारतीय दंड संहिता (IPC) का स्थान लिया। किसी व्यक्ति को ऐसे कानून के तहत दंडित नहीं किया जा सकता जो उसके कृत्य के समय लागू नहीं था, इसलिए दोनों संहिताएँ उपयोग में रहती हैं। केस बताएँ — LawShift तय करता है कौन लागू होता है, फिर धारा का मूल पाठ दिखाता है।",
  heroCta: "एक केस लिखें",
  heroChecks: "उत्तर कैसे जाँचे जाते हैं",
  audience:
    "कानून के छात्रों, कनिष्ठ अधिवक्ताओं और पत्रकारों के लिए। शोध सहायक: कानूनी सलाह नहीं, और वकील का विकल्प नहीं।",

  docketBefore: "कटऑफ से पहले",
  docketAfter: "कटऑफ पर या बाद में",
  docketIpcName: "भारतीय दंड संहिता, 1860",
  docketBnsName: "भारतीय न्याय संहिता, 2023",
  docketCaption:
    "हमारे स्वयं के परीक्षणों से दर्ज। केवल तारीख तय करती है कि केस किस ओर पड़ता है।",
  docketTry: "यह केस आज़माएँ",
  case1Facts: "एक किताबों की दुकान का मालिक पहली बार अश्लील पत्रिकाएँ बेचता है।",
  case1ResultNote: "अश्लील पुस्तकों की बिक्री",
  case2Facts:
    "एक दंगा जमींदार के हित में होता है और एजेंट उसे रोकने में विफल रहता है।",
  case2ResultNote: "उस भूमि के मालिक/अधिभोगी आदि का दायित्व जहाँ दंगा होता है",
  case3Facts: "एक व्यक्ति नकली मुद्रा नोटों के साथ पाया जाता है।",
  case3ResultNote:
    "तीन अपराध लगभग समान रूप से फिट बैठते हैं, इसलिए यह पूछता है कि आपका मतलब कौन-सा है",
  compareTitle:
    "एक ही अपराध, दो संहिताएँ",
  compareLead:
    "शुरुआती समयरेखा का पहला मामला IPC 292 के अंतर्गत आता है। यदि यह 1 जुलाई 2024 को या उसके बाद हुआ होता, तो यह BNS 294 के अंतर्गत आता। दोनों पाठ इस प्रकार हैं।",
  compareIpcSpan:
    "30 जून 2024 तक लागू",
  compareBnsSpan:
    "1 जुलाई 2024 से लागू",
  compareSwap:
    "1 जुलाई 2024",
  compareRow1:
    "अश्लील किसे माना जाता है",
  compareRow2:
    "पहली दोषसिद्धि पर दंड",
  compareMapped:
    "मैपिंग तालिका IPC 292 → BNS 294 को सीधा, एक-से-एक मिलान दर्ज करती है।",
  compareChanged:
    "दोनों पाठों में जो शब्द अलग हैं, वे रेखांकित किए गए हैं।",
  compareSource:
    "IPC–BNS मैपिंग तालिका (nandhakumarg/IPC_and_BNS_transformation) से उद्धृत। ... छोड़े गए शब्द दर्शाता है, और फ़ुटनोट चिह्न हटा दिए गए हैं। यह समुदाय-संचालित डेटासेट है, इसलिए जो भी महत्वपूर्ण हो उसे आधिकारिक पाठ से जाँच लें।",

  chatTitle: "एक केस पर आज़माएँ",
  chatLead:
    "क्या हुआ और कब — बताएँ। तारीख कानून तय करती है; अगर आप छोड़ दें तो LawShift पूछेगा।",
  chatTip1: "तारीख पूरा लिखें, जैसे 15 March 2024।",
  chatTip2: "तथ्य साधारण शब्दों में लिखें। धारा का नाम भी दे सकते हैं।",
  chatTip3:
    "हर उत्तर के नीचे स्रोत पाठ खोलकर पढ़ें। वही असली जाँच है।",

  howTitle: "आपके प्रश्न के साथ क्या होता है",
  howLead:
    "चार चरण, हमेशा इसी क्रम में। केवल अंतिम चरण भाषा मॉडल से कुछ लिखता है।",
  step1Title: "तारीख खोजें",
  step1Who: "निर्धारित नियम, कोई मॉडल नहीं",
  step1Body:
    "LawShift आपके विवरण से अपराध की तारीख पढ़ता है। अगर तारीख नहीं है, या दो तरह से पढ़ी जा सकती है — जैसे 07-01-2024 — तो अनुमान लगाने के बजाय आपसे पूछता है।",
  step2Title: "संहिता चुनें",
  step2Who: "एक तारीख तुलना",
  step2Body:
    "1 जुलाई 2024 से पहले भारतीय दंड संहिता लागू होती है। उस दिन या बाद में भारतीय न्याय संहिता। यह कोड में लिखी एक तुलना है। प्रक्रिया आगे कुछ भी इसे ओवरराइड नहीं कर सकती।",
  step3Title: "धारा खोजें",
  step3Who: "खोज, केवल उसी संहिता में",
  step3Body:
    "यह केवल चरण दो में चुनी संहिता में खोजता है, ताकि IPC 201 और BNS 201 कभी मिल न सकें। जब दो या अधिक धाराएँ लगभग समान स्कोर करें, तो प्रत्येक दिखाकर पूछता है कि आपका मतलब कौन-सी है।",
  step4Title: "लिखें और जाँचें",
  step4Who: "भाषा मॉडल",
  step4Body:
    "एक छोटा मॉडल केवल दी गई धारा से Issue, Rule, Application और Conclusion लिखता है। फिर एक बड़ा मॉडल जाँचता है कि निष्कर्ष नियम से निकलता है या नहीं, और अगर नहीं तो झंडा लगाता है।",

  checksTitle: "जब निश्चित नहीं, तो कहता है",
  checksLead:
    "आत्मविश्वास से गलत उत्तर कानूनी उपकरण की सबसे बुरी बात है। LawShift अनिश्चित दिखने के लिए बना है जब वह अनिश्चित हो।",
  outcome1When: "आप तारीख छोड़ देते हैं",
  outcome1Then:
    "यह पूछता है कि यह कब हुआ, क्योंकि बिना तारीख के कौन-सा कानून लागू होता है नहीं बता सकता।",
  outcome2When: "कई धाराएँ समान रूप से फिट बैठती हैं",
  outcome2Then: "यह उनकी शुरुआती पंक्तियों के साथ सूची दिखाता है और आपके चुनाव का इंतज़ार करता है।",
  outcome3When: "निष्कर्ष नियम से नहीं निकलता हो सकता",
  outcome3Then:
    "उत्तर के पास “Worth double-checking” जैसा नोट दिखता है, कारण के साथ।",
  outcome4When: "कुछ मेल नहीं खाता, या लेखन विफल होता है",
  outcome4Then:
    "यह साफ कहता है। खाली जगह भरने के लिए कोई दिखावटी उत्तर नहीं बनाता।",
  checkerTitle: "जाँचकर्ता कितना अच्छा है?",
  checkerP1:
    "हमने 40 उत्तर हाथ से पढ़े। पाँच में निष्कर्ष नियम से नहीं निकला। जाँचकर्ता ने पाँचों को चिह्नित किया, और दस अच्छे उत्तरों को भी। बाद में उन पाँच को लाइव चलाया तो दो पकड़े।",
  checkerP2:
    "इसलिए यह दूसरा मत है, अंतिम फैसला नहीं। यह वैधानिक पाठ के पास झंडा लगाता है और उत्तर छिपाता या रोकता नहीं।",

  evidenceTitle: "हमने क्या मापा, और बारीकियाँ",
  evidenceLead:
    "नीचे हर परिणाम परियोजना में सहेजी परीक्षण दौड़ से है। हर परिणाम के साथ यह भी है कि वह क्या नहीं दिखाता।",
  evidenceColAsked: "हमने पूछा",
  evidenceColFound: "क्या मिला",
  evidenceColFine: "बारीकियाँ",
  evidence1Asked: "क्या यह सही संहिता चुनता है?",
  evidence1Result: "हाँ, हर बार। नियम केवल तारीख की तुलना 1 जुलाई 2024 से करता है।",
  evidence1Fine:
    "460 परीक्षण प्रश्नों पर। यहाँ “सही” उसी नियम से परिभाषित है, इसलिए यह दिखाता है कि नियम लगातार लागू होता है; यह हर तारीख सही पढ़ी गई इसकी जाँच नहीं है। मुक्त पाठ से तारीख पढ़ना 30 में से 30 वास्तविक और 14 में से 14 कठिन प्रश्नों पर सही रहा।",
  evidence2Asked: "क्या यह सही धारा ढूँढता है?",
  evidence2Result:
    "हर 100 held-out प्रश्नों में से 84 में सही धारा उसके पाँच परिणामों में थी।",
  evidence2Fine:
    "ये वैधानिक प्रश्नोत्तर शैली के थे। अलग 85 साधारण प्रश्नों पर आँकड़ा लगभग 66 में 100 था। उत्तर उसके पहले चयन से लिखा जाता है, जो हमेशा सही नहीं होता। इसलिए हर उत्तर के नीचे धारा का अपना पाठ रहता है।",
  evidence3Asked: "क्या यह कानून गढ़ता है?",
  evidence3Result:
    "हाथ से पढ़े 40 उत्तरों में नहीं: कोई बनाई धारा नहीं, कोई उद्धरण जो स्रोत में न हो।",
  evidence3Fine:
    "वे 40 सही धारा देकर लिखे गए, इसलिए यह लेखन चरण जाँचता है, खोज नहीं। नमूना छोटा है। 40 में से 5 में निष्कर्ष फिर भी नियम से नहीं निकला।",
  evidenceMoreBefore: "मेट्रिक्स, डेटासेट और माप विधि",
  evidenceMoreLink: "अनुसंधान नोट्स",

  limitsTitle: "यह कहाँ रुकता है",
  limit1Title: "यह कानूनी सलाह नहीं है",
  limit1Body:
    "LawShift संहिता तेज़ी से पढ़ने में मदद करता है। यह साक्ष्य, केस लॉ या प्रक्रिया नहीं तौलता, और वकील का स्थान नहीं लेता।",
  limit2Title: "कटऑफ के दोनों ओर फैला केस एक उत्तर पाता है",
  limit2Body:
    "अगर कुछ 1 जुलाई 2024 से पहले शुरू होकर बाद में जारी रहा, LawShift एक तारीख लेकर एक संहिता लौटाता है। ऐसे मामलों का डिटेक्टर प्रोटोटाइप है (9 उदाहरणों पर)। उत्पाद में अभी नहीं है।",
  limit3Title: "कटऑफ से पहले केवल IPC खोजी जाती है",
  limit3Body:
    "पुरानी दंड प्रक्रिया संहिता और साक्ष्य अधिनियम का पाठ शामिल नहीं है।",
  limit4Title: "हिंदी और मराठी मशीन-अनुवाद हैं",
  limit4Body:
    "अनुवाद कानूनी विश्लेषण के बाद होता है, इसलिए चुनी धारा नहीं बदल सकता। फिर भी अपूर्ण हो सकता है। ज़रूरी हो तो अंग्रेज़ी देखें।",

  skipLink: "मुख्य सामग्री पर जाएँ",
  evidence1Fig: "460 में से 460",
  evidence3Fig: "40 में से 0",
  waffleLabelA: "क़ानून-शैली के प्रश्न",
  waffleLabelB: "सरल भाषा में लिखे प्रश्न",
  waffleHit: "शीर्ष पाँच में सही धारा",
  waffleMiss: "शीर्ष पाँच में नहीं",
  waffleFigA: "100 में से 84",
  waffleFigB: "100 में से लगभग 66",
  stripTitle: "हाथ से पढ़े 40 उत्तरों पर जाँचकर्ता",
  stripCaught: "निष्कर्ष नहीं बैठा, फ़्लैग हुआ (5)",
  stripFalse: "उत्तर ठीक था, फिर भी फ़्लैग हुआ (10)",
  stripClear: "उत्तर ठीक था, फ़्लैग नहीं हुआ (25)",
  footerDisclaimer:
    "LawShift एक सूचनात्मक शोध उपकरण है। यह कानूनी सलाह नहीं है और वकील का विकल्प नहीं। महत्वपूर्ण बातें BNS, BNSS, BSA और IPC के आधिकारिक पाठ से जाँचें।",
  footerCredits:
    "GSMS-B के वैधानिक पाठ व प्रश्न सेट, nandhakumarg का IPC–BNS मैपिंग, GovIntel और nyaya-eval-v0 पर आधारित; अनुवाद AI4Bharat IndicTrans2 से।",
};

const mr: LandingCopy = {
  navHow: "हे कसे काम करते",
  navEvidence: "आम्ही काय मोजले",
  navAbout: "संशोधन नोंदी",
  answersIn: "उत्तराची भाषा",
  tryACase: "एक खटला वापरून पहा",

  heroTitle: "घटना झाली त्या दिवशी कोणता कायदा लागू होतो हे ठरते.",
  heroLead:
    "१ जुलै २०२४ रोजी भारतीय न्याय संहिता (BNS) ने भारतीय दंड संहिता (IPC) ची जागा घेतली. कृत्य करताना लागू नसलेल्या कायद्याने शिक्षा होऊ शकत नाही, म्हणून दोन्ही संहिता वापरात राहतात. खटला सांगा — LawShift कोणता लागू होतो ते ठरवतो आणि कलमाचा मूळ मजकूर दाखवतो.",
  heroCta: "एक खटला लिहा",
  heroChecks: "उत्तरे कशी तपासली जातात",
  audience:
    "कायद्याच्या विद्यार्थ्यांसाठी, कनिष्ठ अधिवक्त्यांसाठी आणि पत्रकारांसाठी. संशोधन सहाय्यक: कायदेशीर सल्ला नाही, आणि वकिलाचा पर्याय नाही.",

  docketBefore: "कटऑफपूर्वी",
  docketAfter: "कटऑफच्या दिवशी किंवा नंतर",
  docketIpcName: "भारतीय दंड संहिता, १८६०",
  docketBnsName: "भारतीय न्याय संहिता, २०२३",
  docketCaption:
    "आमच्या स्वतःच्या चाचण्यांतून नोंद. फक्त तारीख ठरवते की खटला कुठल्या बाजूला पडतो.",
  docketTry: "हा खटला वापरून पहा",
  case1Facts: "एक पुस्तकाच्या दुकानाचा मालक प्रथमच अश्लील मासिके विकतो.",
  case1ResultNote: "अश्लील पुस्तकांची विक्री",
  case2Facts:
    "जमीनदाराच्या फायद्यासाठी दंगा होतो आणि एजंट तो रोखण्यात अपयशी ठरतो.",
  case2ResultNote: "ज्या जमिनीवर दंगा होतो त्या मालक/भोगवटादार इत्यादींची जबाबदारी",
  case3Facts: "एका व्यक्तीकडे बनावट चलन नोटा सापडतात.",
  case3ResultNote:
    "तीन गुन्हे जवळपास सारखे बसतात, म्हणून तुम्हाला कोणता अभिप्रेत आहे ते विचारते",
  compareTitle:
    "एकच गुन्हा, दोन संहिता",
  compareLead:
    "सुरुवातीच्या कालरेषेतील पहिले प्रकरण IPC 292 अंतर्गत येते. ते 1 जुलै 2024 रोजी किंवा त्यानंतर घडले असते, तर BNS 294 अंतर्गत आले असते. दोन्ही मजकूर असे आहेत.",
  compareIpcSpan:
    "30 जून 2024 पर्यंत लागू",
  compareBnsSpan:
    "1 जुलै 2024 पासून लागू",
  compareSwap:
    "1 जुलै 2024",
  compareRow1:
    "अश्लील कशाला मानले जाते",
  compareRow2:
    "पहिल्या दोषसिद्धीवर शिक्षा",
  compareMapped:
    "मॅपिंग तक्ता IPC 292 → BNS 294 ही थेट, एक-ते-एक जुळणी नोंदवतो.",
  compareChanged:
    "दोन्ही मजकुरांत जे शब्द वेगळे आहेत ते अधोरेखित केले आहेत.",
  compareSource:
    "IPC–BNS मॅपिंग तक्त्यातून (nandhakumarg/IPC_and_BNS_transformation) उद्धृत. ... सोडलेले शब्द दर्शवतो आणि तळटीप चिन्हे काढली आहेत. हा समुदायाने सांभाळलेला डेटासेट आहे, म्हणून महत्त्वाचे काहीही अधिकृत मजकुराशी पडताळा.",

  chatTitle: "एक खटल्यावर वापरून पहा",
  chatLead:
    "काय झाले आणि केव्हा ते सांगा. तारीख कायदा ठरवते; सोडली तर LawShift विचारेल.",
  chatTip1: "तारीख पूर्ण लिहा, जसे 15 March 2024.",
  chatTip2: "तथ्ये साध्या शब्दांत लिहा. कलमाचे नावही देऊ शकता.",
  chatTip3:
    "प्रत्येक उत्तराखाली स्रोत मजकूर उघडून वाचा. तीच खरी तपासणी आहे.",

  howTitle: "तुमच्या प्रश्नाचे काय होते",
  howLead:
    "चार टप्पे, नेहमी याच क्रमाने. फक्त शेवटचा टप्पा भाषा मॉडेलने काही लिहितो.",
  step1Title: "तारीख शोधा",
  step1Who: "ठरलेले नियम, मॉडेल नाही",
  step1Body:
    "LawShift तुमच्या वर्णनातून गुन्ह्याची तारीख वाचतो. तारीख नसेल, किंवा दोन रीतीने वाचता येईल — जसे 07-01-2024 — तर अंदाज न करता विचारते.",
  step2Title: "संहिता निवडा",
  step2Who: "एक तारीख तुलना",
  step2Body:
    "१ जुलै २०२४ पूर्वी भारतीय दंड संहिता लागू. त्या दिवशी किंवा नंतर भारतीय न्याय संहिता. ही कोडमधील एक तुलना आहे. पुढील प्रक्रिया ती बदलू शकत नाही.",
  step3Title: "कलम शोधा",
  step3Who: "शोध, फक्त त्या संहितेत",
  step3Body:
    "टप्पा दोनमध्ये निवडलेल्या संहितेतच शोधते, त्यामुळे IPC २०१ आणि BNS २०१ कधीच मिसळत नाहीत. दोन किंवा अधिक कलमे जवळपास समान गुण मिळवतील तर प्रत्येकी दाखवून विचारते.",
  step4Title: "लिहा आणि तपासा",
  step4Who: "भाषा मॉडेल्स",
  step4Body:
    "लहान मॉडेल फक्त दिलेल्या कलमावरून Issue, Rule, Application आणि Conclusion लिहिते. नंतर मोठे मॉडेल निष्कर्ष नियमातून येतो का ते तपासते; नसेल तर ध्वजांकित करते.",

  checksTitle: "जेव्हा खात्री नसेल तेव्हा सांगते",
  checksLead:
    "आत्मविश्वासाने चुकीचे उत्तर कायदेशीर साधनातील सर्वात वाईट गोष्ट आहे. LawShift अनिश्चित असल्यास अनिश्चित दिसण्यासाठी बनवले आहे.",
  outcome1When: "तुम्ही तारीख सोडता",
  outcome1Then:
    "हे कधी घडले ते विचारते, कारण तारखेशिवाय कोणता कायदा लागू हे सांगता येत नाही.",
  outcome2When: "अनेक कलमे समान बसतात",
  outcome2Then: "त्यांच्या सुरुवातीच्या ओळींसह यादी दाखवते आणि तुमची निवड वाटते.",
  outcome3When: "निष्कर्ष नियमातून येत नसेल",
  outcome3Then:
    "उत्तराशेजारी “Worth double-checking” सारखी नोंद कारणासह दिसते.",
  outcome4When: "काही जुळत नाही, किंवा लेखन अयशस्वी",
  outcome4Then:
    "ते स्पष्ट सांगते. रिकामी जागा भरण्यासाठी बनावट उत्तर तयार करत नाही.",
  checkerTitle: "तपासकर्ता किती चांगला आहे?",
  checkerP1:
    "आम्ही ४० उत्तरे हाताने वाचली. पाचमध्ये निष्कर्ष नियमातून आला नाही. तपासकर्त्याने पाचही चिन्हांकित केली, आणि दहा चांगली उत्तरेही. नंतर ती पाच लाइव्ह चालवली तर दोन पकडली.",
  checkerP2:
    "म्हणून हे दुसरे मत आहे, अंतिम निकाल नाही. वैधानिक मजकुराशेजारी ध्वज लावते आणि उत्तर लपवत किंवा रोखत नाही.",

  evidenceTitle: "आम्ही काय मोजले, आणि तपशील",
  evidenceLead:
    "खालील प्रत्येक निकाल प्रकल्पात साठवलेल्या चाचणी धावातून आहे. प्रत्येकसोबत ते काय दाखवत नाही तेही आहे.",
  evidenceColAsked: "आम्ही विचारले",
  evidenceColFound: "काय सापडले",
  evidenceColFine: "तपशील",
  evidence1Asked: "योग्य संहिता निवडते का?",
  evidence1Result: "होय, प्रत्येक वेळी. नियम फक्त तारखेची १ जुलै २०२४ शी तुलना करतो.",
  evidence1Fine:
    "४६० चाचणी प्रश्नांवर. येथे “योग्य” त्याच नियमाने परिभाषित आहे, त्यामुळे नियम सातत्याने लागू होतो हे दिसते; प्रत्येक तारीख योग्य वाचली गेली हे नाही. मुक्त मजकुरातून तारीख वाचणे ३० पैकी ३० खऱ्या आणि १४ पैकी १४ कठीण प्रश्नांवर बरोबर होते.",
  evidence2Asked: "योग्य कलम सापडते का?",
  evidence2Result:
    "दर १०० held-out प्रश्नांपैकी ८४ मध्ये योग्य कलम त्याच्या पाच निकालांत होते.",
  evidence2Fine:
    "हे वैधानिक प्रश्नोत्तर शैलीचे होते. वेगळ्या ८५ साध्या प्रश्नांवर आकडा सुमारे ६६ पैकी १०० होता. उत्तर पहिल्या निवडीवरून लिहिले जाते, जे नेहमी योग्य नसते. म्हणून प्रत्येक उत्तराखाली कलमाचा स्वतःचा मजकूर असतो.",
  evidence3Asked: "कायदा बनवते का?",
  evidence3Result:
    "हाताने वाचलेल्या ४० उत्तरांत नाही: बनावट कलमे नाहीत, स्रोतात नसलेली उद्धरणे नाहीत.",
  evidence3Fine:
    "ती ४० योग्य कलम देऊन लिहिली, म्हणून लेखन टप्पा तपासतो, शोध नाही. नमुना लहान आहे. ४० पैकी ५ मध्ये निष्कर्ष तरीही नियमातून आला नाही.",
  evidenceMoreBefore: "मेट्रिक्स, डेटासेट आणि मोजमाप पद्धत",
  evidenceMoreLink: "संशोधन नोंदींवर",

  limitsTitle: "हे कुठे थांबते",
  limit1Title: "हे कायदेशीर सल्ला नाही",
  limit1Body:
    "LawShift संहिता जलद वाचण्यास मदत करते. पुरावा, केस लॉ किंवा प्रक्रिया तोलत नाही, आणि वकिलाची जागा घेत नाही.",
  limit2Title: "कटऑफ ओलांडणारा खटला एक उत्तर मिळवतो",
  limit2Body:
    "काही १ जुलै २०२४ पूर्वी सुरू होऊन नंतर सुरू राहिले तर LawShift एक तारीख घेऊन एक संहिता परत करते. अशा प्रकरणांचा डिटेक्टर प्रोटोटाइप आहे (९ उदाहरणे). उत्पादनात अद्याप नाही.",
  limit3Title: "कटऑफपूर्वी फक्त IPC शोधली जाते",
  limit3Body:
    "जुनी दंड प्रक्रिया संहिता आणि साक्षी अधिनियम मजकूर समाविष्ट नाही.",
  limit4Title: "हिंदी आणि मराठी मशीन-अनुवाद आहेत",
  limit4Body:
    "अनुवाद कायदेशीर विश्लेषणानंतर होतो, त्यामुळे निवडलेले कलम बदलू शकत नाही. तरीही अपूर्ण असू शकते. गरज असेल तर इंग्रजी तपासा.",

  skipLink: "मुख्य मजकुराकडे जा",
  evidence1Fig: "460 पैकी 460",
  evidence3Fig: "40 पैकी 0",
  waffleLabelA: "कायद्याच्या शैलीतील प्रश्न",
  waffleLabelB: "साध्या भाषेतील प्रश्न",
  waffleHit: "पहिल्या पाचांत योग्य कलम",
  waffleMiss: "पहिल्या पाचांत नाही",
  waffleFigA: "100 पैकी 84",
  waffleFigB: "100 पैकी सुमारे 66",
  stripTitle: "हाताने वाचलेल्या 40 उत्तरांवर तपासनीस",
  stripCaught: "निष्कर्ष जुळला नाही, ध्वजांकित (5)",
  stripFalse: "उत्तर बरोबर होते, तरी ध्वजांकित (10)",
  stripClear: "उत्तर बरोबर होते, ध्वजांकित नाही (25)",
  footerDisclaimer:
    "LawShift माहितीपूर्ण संशोधन साधन आहे. हे कायदेशीर सल्ला नाही आणि वकिलाचा पर्याय नाही. महत्त्वाचे मुद्दे BNS, BNSS, BSA आणि IPC च्या अधिकृत मजकुराशी तपासा.",
  footerCredits:
    "GSMS-B चे वैधानिक मजकूर व प्रश्न संच, nandhakumarg चे IPC–BNS मॅपिंग, GovIntel आणि nyaya-eval-v0 वर आधारित; अनुवाद AI4Bharat IndicTrans2 ने.",
};

const DICTS: Record<Lang, LandingCopy> = { en, hi, mr };

export function getLandingCopy(lang: Lang): LandingCopy {
  return DICTS[lang] ?? en;
}
