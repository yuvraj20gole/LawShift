import type { Lang } from "./prefs";

/** Copy for the account area (EN / HI / MR). Hindi and Marathi are drafts and need native review. */
export type DashboardCopy = {
  navLabel: string;
  menu: string;
  navWorkspace: string;
  navMapping: string;
  navHistory: string;
  navDocuments: string;
  navRulings: string;
  navSettings: string;
  logout: string;


  describeCase: string;
  open: string;
  verOk: string;
  verFlag: string;
  codeIpc: string;
  codeBns: string;

  wsTitle: string;
  wsLede: string;

  hiTitle: string;
  hiLede: string;
  hiSearch: string;
  hiSearchHint: string;
  hiFilter: string;
  fAll: string;
  fIpc: string;
  fBns: string;
  fStarred: string;
  /** Author draft — needs native review (HI/MR). */
  fFlagged: string;
  colAsked: string;
  colOffence: string;
  colCode: string;
  colSection: string;
  colState: string;
  colAction: string;
  colStar: string;
  star: (label: string) => string;
  unstar: (label: string) => string;
  hiCount: (n: number) => string;
  hiEmptyTitle: string;
  hiEmptyBody: string;
  hiNoMatchTitle: string;
  hiNoMatchBody: string;
  hiStarEmptyTitle: string;
  hiStarEmptyBody: string;
  /** Author draft — needs native review (HI/MR). */
  hiFlagEmptyTitle: string;
  /** Author draft — needs native review (HI/MR). */
  hiFlagEmptyBody: string;
  clearFilters: string;
  hiSavedNote: string;
  hiLoading: string;
  hiError: string;
  hiRetry: string;
  hiDelete: string;
  hiClearAll: string;
  hiClearTitle: string;
  hiClearBody: string;
  hiClearConfirm: string;
  hiCancel: string;
  hiActionFailed: string;
  stDeleteFailed: string;

  dcTitle: string;

  soonTag: string;
  soonNothing: string;
  soonBack: string;
  mapTitle: string;
  mapWill: string;
  rulTitle: string;
  rulWill: string;

  linkCourt: string;
  linkArchive: string;
  draftBadge: string;
  mapLede: string;
  mapStepCode: string;
  mapFromIpc: string;
  mapFromBns: string;
  mapSectionLabel: string;
  mapSectionHint: string;
  mapSuggestions: string;
  mapLookup: string;
  mapLooking: string;
  mapOffline: string;
  mapNotFound: (code: string, section: string) => string;
  mapResultFor: (code: string, section: string) => string;
  mapTypeLabel: string;
  mapTypeSection: string;
  mapTypePartial: (sub: string) => string;
  mapTypeMerged: string;
  mapTypeDropped: string;
  mapEntry: (raw: string) => string;
  mapNoEquiv: string;
  mapBnsOnly: string;
  mapManyIpc: string;
  mapDiffNote: string;
  mapNote: string;
  mapAsk: string;
  mapCaveat: string;
  mapIpcSpan: string;
  mapBnsSpan: string;
  mapSwap: string;
  rlLede: string;
  rlSearch: string;
  rlSearchHint: string;
  rlBranch: string;
  bAll: string;
  bIpcBns: string;
  bCriminal: string;
  bCivil: string;
  rlCourt: string;
  cAll: string;
  cSupreme: string;
  cBombay: string;
  rlBench: string;
  rlAllBenches: string;
  benchTip: (code: string) => string;
  benchTipNone: string;
  rlBackgroundTitle: string;
  rlFeaturedTitle: string;
  rlCurated: string;
  rlLastReviewed: (d: string) => string;
  rlEmptyTitle: string;
  rlEmptyBody: string;
  rlClear: string;
  rlShowMore: string;
  rlShowing: (n: number, total: number) => string;
  rlCurrentTo: (d: string) => string;
  rlBatches: string;
  rlScSample: (n: number) => string;
  rlBombaySample: (perWeek: number, weeks: number) => string;
  rlAttribution: string;
  rlCaseType: string;
  rlCaseNumber: string;
  rlBenchCol: string;
  rlDecided: string;
  rlOutcome: string;
  rlLoading: string;
  rlFailed: string;
  linkOther: (site: string) => string;
  dateToVerify: string;
  stTitle: string;
  stLede: string;
  stEmailTitle: string;
  stEmailNote: string;
  stLangTitle: string;
  stLangNote: string;
  stPasswordTitle: string;
  stCurrent: string;
  stNew: string;
  stConfirm: string;
  stUpdate: string;
  stUpdating: string;
  stUpdated: string;
  stDeleteTitle: string;
  stDeleteBody: string;
  stDeleteType: (email: string) => string;
  stDeleteButton: string;
  stDeleteDone: string;
};

const en: DashboardCopy = {
  navLabel: "Account",
  menu: "Menu",
  navWorkspace: "Workspace",
  navMapping: "Mapping",
  navHistory: "Case history",
  navDocuments: "Documents",
  navRulings: "Rulings",
  navSettings: "Settings",
  logout: "Log out",


  describeCase: "Describe a case",
  open: "Open",
  verOk: "No inconsistency detected",
  verFlag: "Worth double-checking",
  codeIpc: "IPC",
  codeBns: "BNS",

  wsTitle: "Workspace",
  wsLede: "Describe what happened and when. Answers come from the statute text.",

  hiTitle: "Case history",
  hiLede: "Every question you have asked, with the code it was routed to.",
  hiSearch: "Search cases",
  hiSearchHint: "Search by section, title or question",
  hiFilter: "Code",
  fAll: "All",
  fIpc: "IPC",
  fBns: "BNS",
  fStarred: "Starred",
  fFlagged: "Flagged", // author draft — needs native review
  colAsked: "Asked",
  colOffence: "Offence date",
  colCode: "Code",
  colSection: "Section",
  colState: "Check",
  colAction: "Action",
  colStar: "Star",
  star: (l) => `Star ${l}`,
  unstar: (l) => `Remove star from ${l}`,
  hiCount: (n) => `${n} ${n === 1 ? "case" : "cases"}`,
  hiEmptyTitle: "No cases yet",
  hiEmptyBody: "Questions you ask in the workspace will be listed here with their section and check result.",
  hiNoMatchTitle: "No cases match",
  hiNoMatchBody: "Try a different word, or show every case.",
  hiStarEmptyTitle: "No starred cases",
  hiStarEmptyBody: "Star a case to keep it here.",
  hiFlagEmptyTitle: "No flagged answers.", // author draft — needs native review
  hiFlagEmptyBody: "Answers marked “Worth double-checking” will appear here.", // author draft — needs native review
  clearFilters: "Clear search and filter",
  hiSavedNote: "Your questions are saved in your account. Deleting your account removes them.",
  hiLoading: "Loading your history…",
  hiError: "Your history couldn't be loaded. Check your connection, then try again.",
  hiRetry: "Try again",
  hiDelete: "Delete",
  hiClearAll: "Clear all history",
  hiClearTitle: "Delete all your saved history?",
  hiClearBody: "This removes every saved question from your account. It can't be undone.",
  hiClearConfirm: "Yes, delete everything",
  hiCancel: "Cancel",
  hiActionFailed: "That didn't work. Try again.",
  stDeleteFailed: "Your account could not be deleted. You are still logged in. Try again.",

  dcTitle: "Documents",

  soonTag: "Coming next",
  soonNothing: "Nothing is listed here yet, because this page isn't built.",
  soonBack: "Back to Workspace",
  mapTitle: "Mapping",
  mapWill:
    "This page will show how an IPC section maps to its BNS section: whether the match is one-to-one, partial, merged or dropped, with both texts side by side, from the IPC–BNS mapping table.",
  rulTitle: "Rulings",
  rulWill:
    "This page will list court judgments from the archive, which you can filter by court and by criminal or civil, plus a Background group of judgments on which code applies. Background entries stay marked as drafts until they have been checked.",

  linkCourt: "Read the court's copy",
  linkArchive: "Read the judgment (archive copy)",
  draftBadge: "Draft: not yet checked",
  mapLede: "Look up the corresponding section between the IPC and the BNS. This is a lookup in our mapping table, not a chat.",
  mapStepCode: "Which code is your section in?",
  mapFromIpc: "My section is in the IPC",
  mapFromBns: "My section is in the BNS",
  mapSectionLabel: "Section number",
  mapSectionHint: "Type a number or part of a title, for example 292 or obscene",
  mapSuggestions: "Suggestions",
  mapLookup: "Look up",
  mapLooking: "Looking it up…",
  mapOffline: "The lookup couldn't be reached. Check that the service is running, then try again.",
  mapNotFound: (c, s) => `No section "${s}" was found in the ${c}. Check the number.`,
  mapResultFor: (c, s) => `Result for ${c} ${s}`,
  mapTypeLabel: "What the table records",
  mapTypeSection: "Section: one IPC section corresponds to one BNS section.",
  mapTypePartial: (sub) => `Partial: only part of the BNS section corresponds (${sub}).`,
  mapTypeMerged: "Merged: our table records several IPC sections against this one BNS section.",
  mapTypeDropped: "Dropped: our table records this IPC section as repealed in the BNS.",
  mapEntry: (raw) => `The table's own entry reads: “${raw}”.`,
  mapNoEquiv: "No equivalent is recorded in our mapping table.",
  mapBnsOnly: "This BNS section exists, but no IPC section is recorded against it in our table.",
  mapManyIpc: "Several IPC sections are recorded against this BNS section. Every one is shown.",
  mapDiffNote: "Words that differ between the two texts are highlighted.",
  mapNote:
    "This shows the corresponding section. Which code applies to a case depends on the offence date. Check that in the Workspace.",
  mapAsk: "Ask in Workspace",
  mapCaveat:
    "The mapping table is community-maintained, so check the official text. It covers the IPC and the BNS only. IPC text is shown with footnote markers and square brackets removed.",
  mapIpcSpan: "Indian Penal Code, 1860",
  mapBnsSpan: "Bharatiya Nyaya Sanhita, 2023",
  mapSwap: "Recorded as corresponding",
  rlLede: "Court judgments from public archives, plus a short curated list of background and featured judgments.",
  rlSearch: "Search rulings",
  rlSearchHint: "Search by title or case number",
  rlBranch: "Branch",
  bAll: "All",
  bIpcBns: "IPC & BNS",
  bCriminal: "Criminal",
  bCivil: "Civil",
  rlCourt: "Court",
  cAll: "All courts",
  cSupreme: "Supreme Court",
  cBombay: "Bombay High Court",
  rlBench: "Bench",
  rlAllBenches: "All benches",
  benchTip: (code) => `Bench name read from the document header; code as recorded in the archive: ${code}`,
  benchTipNone: "Bench code as recorded in the archive",
  rlBackgroundTitle: "Background: which code applies",
  rlFeaturedTitle: "Featured",
  rlCurated: "A curated list and an archive, not a live feed.",
  rlLastReviewed: (d) => `Last reviewed: ${d}`,
  rlEmptyTitle: "No rulings match",
  rlEmptyBody: "Try a different word, or show every court and branch.",
  rlClear: "Clear search and filters",
  rlShowMore: "Show more",
  rlShowing: (n, t) => `Showing ${n} of ${t}`,
  rlCurrentTo: (d) => `Archive current to ${d}`,
  rlBatches: "The archive updates in batches, so it runs behind the court.",
  rlScSample: (n) => `Shows the ${n} most recent final judgments in the archive, not every judgment.`,
  rlBombaySample: (p, w) =>
    `Shows the ${p} most recent final orders and judgments of each week over the last ${w} weeks, with routine 'disposed off' orders left out. Some weeks have fewer or no records, so this is not a complete list. The archive does not distinguish a full judgment from a short order.`,
  rlAttribution:
    "Dates are as recorded in the archive and can contain errors. Criminal and civil labels are derived from the case type and can be imprecise. The archives are CC BY 4.0, from Dattam Labs and the dataset maintainers. Check the court's own copy.",
  rlCaseType: "Case type",
  rlCaseNumber: "Case number",
  rlBenchCol: "Bench",
  rlDecided: "Decided",
  rlOutcome: "Outcome",
  rlLoading: "Loading rulings…",
  rlFailed: "The archive couldn't be loaded. Check that the service is running, then try again.",
  linkOther: (site) => `Read a copy (${site})`,
  dateToVerify: "Date to verify",

  stTitle: "Settings",
  stLede: "Your account and how LawShift answers you.",
  stEmailTitle: "Email",
  stEmailNote: "This is the address on your account. It can't be changed here.",
  stLangTitle: "Default answer language",
  stLangNote: "Answers are written in English and machine-translated after the legal work is done.",
  stPasswordTitle: "Change password",
  stCurrent: "Current password",
  stNew: "New password",
  stConfirm: "Confirm new password",
  stUpdate: "Update password",
  stUpdating: "Updating…",
  stUpdated: "Password updated.",
  stDeleteTitle: "Delete account",
  stDeleteBody:
    "This deletes your account, your saved case history and your saved documents (the files and your descriptions). It can't be undone.",
  stDeleteType: (e) => `Type ${e} to confirm`,
  stDeleteButton: "Delete account",
  stDeleteDone:
    "Preview: in the live version your account, case history and stored documents would be deleted now.",
};

const hi: DashboardCopy = {
  navLabel: "खाता",
  menu: "मेनू",
  navWorkspace: "कार्यक्षेत्र",
  navMapping: "मैपिंग",
  navHistory: "केस इतिहास",
  navDocuments: "दस्तावेज़",
  navRulings: "निर्णय",
  navSettings: "सेटिंग्स",
  logout: "लॉग आउट",


  describeCase: "एक केस बताएँ",
  open: "खोलें",
  verOk: "कोई असंगति नहीं मिली",
  verFlag: "दोबारा जाँचने योग्य",
  codeIpc: "IPC",
  codeBns: "BNS",

  wsTitle: "कार्यक्षेत्र",
  wsLede: "बताएँ कि क्या हुआ और कब। उत्तर वैधानिक पाठ से आते हैं।",

  hiTitle: "केस इतिहास",
  hiLede: "आपके पूछे हर प्रश्न, और जिस संहिता में वह गया।",
  hiSearch: "केस खोजें",
  hiSearchHint: "धारा, शीर्षक या प्रश्न से खोजें",
  hiFilter: "संहिता",
  fAll: "सभी",
  fIpc: "IPC",
  fBns: "BNS",
  fStarred: "तारांकित",
  fFlagged: "फ़्लैग किए गए", // author draft — needs native review
  colAsked: "पूछा गया",
  colOffence: "अपराध की तिथि",
  colCode: "संहिता",
  colSection: "धारा",
  colState: "जाँच",
  colAction: "कार्रवाई",
  colStar: "तारा",
  star: (l) => `${l} को तारांकित करें`,
  unstar: (l) => `${l} से तारा हटाएँ`,
  hiCount: (n) => `${n} केस`,
  hiEmptyTitle: "अभी कोई केस नहीं",
  hiEmptyBody: "कार्यक्षेत्र में आपके पूछे प्रश्न धारा और जाँच परिणाम के साथ यहाँ दिखेंगे।",
  hiNoMatchTitle: "कोई केस मेल नहीं खाता",
  hiNoMatchBody: "कोई दूसरा शब्द आज़माएँ, या सभी केस दिखाएँ।",
  hiStarEmptyTitle: "कोई तारांकित केस नहीं",
  hiStarEmptyBody: "किसी केस को तारांकित करें, वह यहाँ रखा जाएगा।",
  hiFlagEmptyTitle: "कोई फ़्लैग किया उत्तर नहीं।", // author draft — needs native review
  hiFlagEmptyBody: "“दोबारा जाँचने योग्य” चिह्नित उत्तर यहाँ दिखेंगे।", // author draft — needs native review
  clearFilters: "खोज और फ़िल्टर हटाएँ",
  hiSavedNote: "आपके प्रश्न आपके खाते में सहेजे जाते हैं। खाता हटाने पर वे हट जाते हैं।",
  hiLoading: "आपका इतिहास लोड हो रहा है…",
  hiError: "आपका इतिहास लोड नहीं हो सका। कनेक्शन जाँचें, फिर दोबारा कोशिश करें।",
  hiRetry: "दोबारा कोशिश करें",
  hiDelete: "हटाएँ",
  hiClearAll: "पूरा इतिहास साफ़ करें",
  hiClearTitle: "आपका सहेजा हुआ पूरा इतिहास हटाएँ?",
  hiClearBody: "इससे आपके खाते से हर सहेजा गया प्रश्न हट जाएगा। इसे वापस नहीं किया जा सकता।",
  hiClearConfirm: "हाँ, सब हटाएँ",
  hiCancel: "रद्द करें",
  hiActionFailed: "यह नहीं हो सका। दोबारा कोशिश करें।",
  stDeleteFailed: "आपका खाता हटाया नहीं जा सका। आप अब भी लॉग इन हैं। दोबारा कोशिश करें।",

  dcTitle: "दस्तावेज़",

  soonTag: "आगे आ रहा है",
  soonNothing: "यहाँ अभी कुछ सूचीबद्ध नहीं है, क्योंकि यह पृष्ठ बना नहीं है।",
  soonBack: "कार्यक्षेत्र पर वापस जाएँ",
  mapTitle: "मैपिंग",
  mapWill:
    "यह पृष्ठ दिखाएगा कि IPC की कोई धारा BNS की किस धारा से मेल खाती है: मिलान एक-से-एक है, आंशिक, मिला हुआ या हटा हुआ, दोनों पाठ साथ-साथ, IPC–BNS मैपिंग तालिका से।",
  rulTitle: "निर्णय",
  rulWill:
    "यह पृष्ठ अभिलेखागार से न्यायालयों के निर्णय सूचीबद्ध करेगा, जिन्हें आप न्यायालय और आपराधिक या दीवानी के आधार पर छान सकेंगे, साथ में एक पृष्ठभूमि समूह उन निर्णयों का जो बताते हैं कि कौन-सी संहिता लागू होती है। पृष्ठभूमि प्रविष्टियाँ जाँचे जाने तक मसौदा चिह्नित रहेंगी।",

  linkCourt: "न्यायालय की प्रति पढ़ें",
  linkArchive: "निर्णय पढ़ें (अभिलेखागार प्रति)",
  draftBadge: "मसौदा: अभी जाँचा नहीं गया",
  mapLede: "IPC और BNS के बीच संगत धारा खोजें। यह हमारी मैपिंग तालिका में खोज है, चैट नहीं।",
  mapStepCode: "आपकी धारा किस संहिता में है?",
  mapFromIpc: "मेरी धारा IPC में है",
  mapFromBns: "मेरी धारा BNS में है",
  mapSectionLabel: "धारा संख्या",
  mapSectionHint: "संख्या या शीर्षक का अंश लिखें, जैसे 292 या obscene",
  mapSuggestions: "सुझाव",
  mapLookup: "खोजें",
  mapLooking: "खोजा जा रहा है…",
  mapOffline: "खोज तक पहुँच नहीं हो सकी। जाँचें कि सेवा चल रही है, फिर दोबारा कोशिश करें।",
  mapNotFound: (c, s) => `${c} में धारा "${s}" नहीं मिली। संख्या जाँचें।`,
  mapResultFor: (c, s) => `${c} ${s} का परिणाम`,
  mapTypeLabel: "तालिका क्या दर्ज करती है",
  mapTypeSection: "Section: IPC की एक धारा BNS की एक धारा के अनुरूप है।",
  mapTypePartial: (sub) => `Partial: BNS धारा का केवल एक भाग अनुरूप है (${sub})।`,
  mapTypeMerged: "Merged: हमारी तालिका इस एक BNS धारा के सामने IPC की कई धाराएँ दर्ज करती है।",
  mapTypeDropped: "Dropped: हमारी तालिका इस IPC धारा को BNS में निरस्त के रूप में दर्ज करती है।",
  mapEntry: (raw) => `तालिका की अपनी प्रविष्टि है: “${raw}”।`,
  mapNoEquiv: "हमारी मैपिंग तालिका में कोई समतुल्य दर्ज नहीं है।",
  mapBnsOnly: "यह BNS धारा मौजूद है, लेकिन हमारी तालिका में इसके सामने कोई IPC धारा दर्ज नहीं है।",
  mapManyIpc: "इस BNS धारा के सामने IPC की कई धाराएँ दर्ज हैं। हर एक दिखाई गई है।",
  mapDiffNote: "दोनों पाठों में जो शब्द अलग हैं, वे रेखांकित किए गए हैं।",
  mapNote:
    "यह संगत धारा दिखाता है। किसी केस पर कौन-सी संहिता लागू होगी, यह अपराध की तिथि पर निर्भर है। इसे कार्यक्षेत्र में जाँचें।",
  mapAsk: "कार्यक्षेत्र में पूछें",
  mapCaveat:
    "मैपिंग तालिका समुदाय द्वारा संचालित है, इसलिए आधिकारिक पाठ जाँच लें। यह केवल IPC और BNS को कवर करती है। IPC पाठ से फ़ुटनोट चिह्न और वर्गाकार कोष्ठक हटा दिए गए हैं।",
  mapIpcSpan: "भारतीय दंड संहिता, 1860",
  mapBnsSpan: "भारतीय न्याय संहिता, 2023",
  mapSwap: "अनुरूप के रूप में दर्ज",
  rlLede: "सार्वजनिक अभिलेखागारों से न्यायालयों के निर्णय, साथ में पृष्ठभूमि और चुने हुए निर्णयों की एक छोटी संकलित सूची।",
  rlSearch: "निर्णय खोजें",
  rlSearchHint: "शीर्षक या केस संख्या से खोजें",
  rlBranch: "शाखा",
  bAll: "सभी",
  bIpcBns: "IPC और BNS",
  bCriminal: "आपराधिक",
  bCivil: "दीवानी",
  rlCourt: "न्यायालय",
  cAll: "सभी न्यायालय",
  cSupreme: "सर्वोच्च न्यायालय",
  cBombay: "बॉम्बे उच्च न्यायालय",
  rlBench: "पीठ",
  rlAllBenches: "सभी पीठ",
  benchTip: (code) => `पीठ का नाम दस्तावेज़ के शीर्ष से पढ़ा गया; अभिलेखागार में दर्ज कोड: ${code}`,
  benchTipNone: "अभिलेखागार में दर्ज पीठ कोड",
  rlBackgroundTitle: "पृष्ठभूमि: कौन-सी संहिता लागू होती है",
  rlFeaturedTitle: "चयनित",
  rlCurated: "एक संकलित सूची और एक अभिलेखागार, लाइव फ़ीड नहीं।",
  rlLastReviewed: (d) => `अंतिम समीक्षा: ${d}`,
  rlEmptyTitle: "कोई निर्णय मेल नहीं खाता",
  rlEmptyBody: "कोई दूसरा शब्द आज़माएँ, या सभी न्यायालय और शाखाएँ दिखाएँ।",
  rlClear: "खोज और फ़िल्टर हटाएँ",
  rlShowMore: "और दिखाएँ",
  rlShowing: (n, t) => `${t} में से ${n} दिख रहे हैं`,
  rlCurrentTo: (d) => `अभिलेखागार ${d} तक का है`,
  rlBatches: "अभिलेखागार खेपों में अपडेट होता है, इसलिए वह न्यायालय से पीछे रहता है।",
  rlScSample: (n) => `अभिलेखागार के ${n} सबसे हाल के अंतिम निर्णय दिखाता है, हर निर्णय नहीं।`,
  rlBombaySample: (p, w) =>
    `पिछले ${w} सप्ताहों के हर सप्ताह के ${p} सबसे हाल के अंतिम आदेश और निर्णय दिखाता है, नियमित 'disposed off' आदेशों को छोड़कर। कुछ सप्ताहों में कम या कोई अभिलेख नहीं हैं, इसलिए यह पूरी सूची नहीं है। अभिलेखागार पूर्ण निर्णय और छोटे आदेश में अंतर नहीं करता।`,
  rlAttribution:
    "तिथियाँ अभिलेखागार में दर्ज अनुसार हैं और उनमें त्रुटियाँ हो सकती हैं। आपराधिक और दीवानी लेबल केस के प्रकार से निकाले गए हैं और अशुद्ध हो सकते हैं। अभिलेखागार CC BY 4.0 हैं, Dattam Labs और डेटासेट के रखरखावकर्ताओं से। न्यायालय की अपनी प्रति जाँच लें।",
  rlCaseType: "केस का प्रकार",
  rlCaseNumber: "केस संख्या",
  rlBenchCol: "पीठ",
  rlDecided: "निर्णय की तिथि",
  rlOutcome: "परिणाम",
  rlLoading: "निर्णय लोड हो रहे हैं…",
  rlFailed: "अभिलेखागार लोड नहीं हो सका। जाँचें कि सेवा चल रही है, फिर दोबारा कोशिश करें।",
  linkOther: (site) => `प्रति पढ़ें (${site})`,
  dateToVerify: "तिथि जाँचनी है",

  stTitle: "सेटिंग्स",
  stLede: "आपका खाता और LawShift आपको कैसे उत्तर देता है।",
  stEmailTitle: "ईमेल",
  stEmailNote: "यह आपके खाते का पता है। इसे यहाँ बदला नहीं जा सकता।",
  stLangTitle: "उत्तर की डिफ़ॉल्ट भाषा",
  stLangNote: "उत्तर अंग्रेज़ी में लिखे जाते हैं और कानूनी काम पूरा होने के बाद मशीन-अनुवाद होते हैं।",
  stPasswordTitle: "पासवर्ड बदलें",
  stCurrent: "वर्तमान पासवर्ड",
  stNew: "नया पासवर्ड",
  stConfirm: "नए पासवर्ड की पुष्टि करें",
  stUpdate: "पासवर्ड अपडेट करें",
  stUpdating: "अपडेट हो रहा है…",
  stUpdated: "पासवर्ड अपडेट हो गया।",
  stDeleteTitle: "खाता हटाएँ",
  stDeleteBody:
    "इससे आपका खाता, सहेजा गया केस इतिहास और सहेजे गए दस्तावेज़ (फ़ाइलें और आपके विवरण) हट जाएँगे। इसे वापस नहीं किया जा सकता।",
  stDeleteType: (e) => `पुष्टि के लिए ${e} लिखें`,
  stDeleteButton: "खाता हटाएँ",
  stDeleteDone:
    "पूर्वावलोकन: लाइव संस्करण में आपका खाता, केस इतिहास और सहेजे दस्तावेज़ अभी हटा दिए जाते।",
};

const mr: DashboardCopy = {
  navLabel: "खाते",
  menu: "मेनू",
  navWorkspace: "कार्यक्षेत्र",
  navMapping: "मॅपिंग",
  navHistory: "प्रकरण इतिहास",
  navDocuments: "दस्तऐवज",
  navRulings: "निर्णय",
  navSettings: "सेटिंग्ज",
  logout: "लॉग आउट",


  describeCase: "एक प्रकरण सांगा",
  open: "उघडा",
  verOk: "कोणतीही विसंगती आढळली नाही",
  verFlag: "पुन्हा तपासण्यासारखे",
  codeIpc: "IPC",
  codeBns: "BNS",

  wsTitle: "कार्यक्षेत्र",
  wsLede: "काय घडले आणि कधी ते सांगा. उत्तरे वैधानिक मजकुरातून येतात.",

  hiTitle: "प्रकरण इतिहास",
  hiLede: "तुम्ही विचारलेले प्रत्येक प्रश्न, आणि तो ज्या संहितेकडे गेला.",
  hiSearch: "प्रकरणे शोधा",
  hiSearchHint: "कलम, शीर्षक किंवा प्रश्नाने शोधा",
  hiFilter: "संहिता",
  fAll: "सर्व",
  fIpc: "IPC",
  fBns: "BNS",
  fStarred: "तारांकित",
  fFlagged: "ध्वजांकित", // author draft — needs native review
  colAsked: "विचारले",
  colOffence: "गुन्ह्याची तारीख",
  colCode: "संहिता",
  colSection: "कलम",
  colState: "तपासणी",
  colAction: "कृती",
  colStar: "तारा",
  star: (l) => `${l} ला तारांकित करा`,
  unstar: (l) => `${l} वरील तारा काढा`,
  hiCount: (n) => `${n} प्रकरणे`,
  hiEmptyTitle: "अजून कोणतेही प्रकरण नाही",
  hiEmptyBody: "कार्यक्षेत्रात तुम्ही विचारलेले प्रश्न कलम आणि तपासणी निकालासह येथे दिसतील.",
  hiNoMatchTitle: "कोणतेही प्रकरण जुळत नाही",
  hiNoMatchBody: "वेगळा शब्द वापरून पाहा, किंवा सर्व प्रकरणे दाखवा.",
  hiStarEmptyTitle: "कोणतेही तारांकित प्रकरण नाही",
  hiStarEmptyBody: "एखादे प्रकरण तारांकित करा, ते येथे ठेवले जाईल.",
  hiFlagEmptyTitle: "कोणतेही ध्वजांकित उत्तर नाही.", // author draft — needs native review
  hiFlagEmptyBody: "“पुन्हा तपासण्यासारखे” चिन्हांकित उत्तरे येथे दिसतील.", // author draft — needs native review
  clearFilters: "शोध आणि फिल्टर काढा",
  hiSavedNote: "तुमचे प्रश्न तुमच्या खात्यात जतन केले जातात. खाते हटवल्यास ते हटतात.",
  hiLoading: "तुमचा इतिहास लोड होत आहे…",
  hiError: "तुमचा इतिहास लोड करता आला नाही. कनेक्शन तपासा, मग पुन्हा प्रयत्न करा.",
  hiRetry: "पुन्हा प्रयत्न करा",
  hiDelete: "हटवा",
  hiClearAll: "संपूर्ण इतिहास साफ करा",
  hiClearTitle: "तुमचा जतन केलेला संपूर्ण इतिहास हटवायचा?",
  hiClearBody: "यामुळे तुमच्या खात्यातील प्रत्येक जतन केलेला प्रश्न हटेल. हे परत करता येणार नाही.",
  hiClearConfirm: "होय, सर्व हटवा",
  hiCancel: "रद्द करा",
  hiActionFailed: "ते झाले नाही. पुन्हा प्रयत्न करा.",
  stDeleteFailed: "तुमचे खाते हटवता आले नाही. तुम्ही अजूनही लॉग इन आहात. पुन्हा प्रयत्न करा.",

  dcTitle: "दस्तऐवज",

  soonTag: "पुढे येत आहे",
  soonNothing: "येथे अजून काहीही यादीत नाही, कारण हे पान तयार झालेले नाही.",
  soonBack: "कार्यक्षेत्राकडे परत जा",
  mapTitle: "मॅपिंग",
  mapWill:
    "हे पान दाखवेल की IPC चे एखादे कलम BNS च्या कोणत्या कलमाशी जुळते: जुळणी एक-ते-एक आहे, आंशिक, एकत्रित की वगळलेली, दोन्ही मजकूर शेजारी-शेजारी, IPC–BNS मॅपिंग तक्त्यातून.",
  rulTitle: "निर्णय",
  rulWill:
    "हे पान संग्रहातील न्यायालयांचे निर्णय यादीत देईल, जे तुम्ही न्यायालय आणि फौजदारी किंवा दिवाणी नुसार गाळू शकाल, तसेच कोणती संहिता लागू होते यावरील निर्णयांचा एक पार्श्वभूमी गट. पार्श्वभूमी नोंदी तपासल्या जाईपर्यंत मसुदा म्हणून चिन्हांकित राहतील.",

  linkCourt: "न्यायालयाची प्रत वाचा",
  linkArchive: "निर्णय वाचा (संग्रह प्रत)",
  draftBadge: "मसुदा: अजून तपासलेला नाही",
  mapLede: "IPC आणि BNS मधील संबंधित कलम शोधा. ही आमच्या मॅपिंग तक्त्यातील शोध आहे, चॅट नाही.",
  mapStepCode: "तुमचे कलम कोणत्या संहितेत आहे?",
  mapFromIpc: "माझे कलम IPC मध्ये आहे",
  mapFromBns: "माझे कलम BNS मध्ये आहे",
  mapSectionLabel: "कलम क्रमांक",
  mapSectionHint: "क्रमांक किंवा शीर्षकाचा भाग लिहा, उदा. 292 किंवा obscene",
  mapSuggestions: "सूचना",
  mapLookup: "शोधा",
  mapLooking: "शोधत आहे…",
  mapOffline: "शोधापर्यंत पोहोचता आले नाही. सेवा चालू आहे का ते तपासा, मग पुन्हा प्रयत्न करा.",
  mapNotFound: (c, s) => `${c} मध्ये कलम "${s}" सापडले नाही. क्रमांक तपासा.`,
  mapResultFor: (c, s) => `${c} ${s} चा निकाल`,
  mapTypeLabel: "तक्ता काय नोंदवतो",
  mapTypeSection: "Section: IPC चे एक कलम BNS च्या एका कलमाशी जुळते.",
  mapTypePartial: (sub) => `Partial: BNS कलमाचा फक्त एक भाग जुळतो (${sub}).`,
  mapTypeMerged: "Merged: आमचा तक्ता या एका BNS कलमासमोर IPC ची अनेक कलमे नोंदवतो.",
  mapTypeDropped: "Dropped: आमचा तक्ता हे IPC कलम BNS मध्ये रद्द म्हणून नोंदवतो.",
  mapEntry: (raw) => `तक्त्याची स्वतःची नोंद अशी आहे: “${raw}”.`,
  mapNoEquiv: "आमच्या मॅपिंग तक्त्यात कोणतेही समतुल्य नोंदवलेले नाही.",
  mapBnsOnly: "हे BNS कलम अस्तित्वात आहे, पण आमच्या तक्त्यात त्यासमोर कोणतेही IPC कलम नोंदवलेले नाही.",
  mapManyIpc: "या BNS कलमासमोर IPC ची अनेक कलमे नोंदवली आहेत. प्रत्येक दाखवले आहे.",
  mapDiffNote: "दोन्ही मजकुरांत जे शब्द वेगळे आहेत ते अधोरेखित केले आहेत.",
  mapNote:
    "हे संबंधित कलम दाखवते. एखाद्या प्रकरणाला कोणती संहिता लागू होते ते गुन्ह्याच्या तारखेवर अवलंबून असते. ते कार्यक्षेत्रात तपासा.",
  mapAsk: "कार्यक्षेत्रात विचारा",
  mapCaveat:
    "मॅपिंग तक्ता समुदायाने सांभाळलेला आहे, म्हणून अधिकृत मजकूर तपासा. तो फक्त IPC आणि BNS ला व्यापतो. IPC मजकुरातून तळटीप चिन्हे आणि चौकोनी कंस काढले आहेत.",
  mapIpcSpan: "भारतीय दंड संहिता, १८६०",
  mapBnsSpan: "भारतीय न्याय संहिता, २०२३",
  mapSwap: "संबंधित म्हणून नोंदवलेले",
  rlLede: "सार्वजनिक संग्रहांतील न्यायालयांचे निर्णय, तसेच पार्श्वभूमी आणि निवडक निर्णयांची एक छोटी निवडलेली यादी.",
  rlSearch: "निर्णय शोधा",
  rlSearchHint: "शीर्षक किंवा प्रकरण क्रमांकाने शोधा",
  rlBranch: "शाखा",
  bAll: "सर्व",
  bIpcBns: "IPC आणि BNS",
  bCriminal: "फौजदारी",
  bCivil: "दिवाणी",
  rlCourt: "न्यायालय",
  cAll: "सर्व न्यायालये",
  cSupreme: "सर्वोच्च न्यायालय",
  cBombay: "मुंबई उच्च न्यायालय",
  rlBench: "खंडपीठ",
  rlAllBenches: "सर्व खंडपीठे",
  benchTip: (code) => `खंडपीठाचे नाव दस्तऐवजाच्या शीर्षावरून वाचले; संग्रहात नोंदवलेला कोड: ${code}`,
  benchTipNone: "संग्रहात नोंदवलेला खंडपीठ कोड",
  rlBackgroundTitle: "पार्श्वभूमी: कोणती संहिता लागू होते",
  rlFeaturedTitle: "निवडक",
  rlCurated: "एक निवडलेली यादी आणि एक संग्रह, थेट फीड नाही.",
  rlLastReviewed: (d) => `शेवटचा आढावा: ${d}`,
  rlEmptyTitle: "कोणताही निर्णय जुळत नाही",
  rlEmptyBody: "वेगळा शब्द वापरून पाहा, किंवा सर्व न्यायालये आणि शाखा दाखवा.",
  rlClear: "शोध आणि फिल्टर काढा",
  rlShowMore: "अधिक दाखवा",
  rlShowing: (n, t) => `${t} पैकी ${n} दिसत आहेत`,
  rlCurrentTo: (d) => `संग्रह ${d} पर्यंतचा आहे`,
  rlBatches: "संग्रह टप्प्याटप्प्याने अपडेट होतो, म्हणून तो न्यायालयाच्या मागे असतो.",
  rlScSample: (n) => `संग्रहातील ${n} सर्वात अलीकडील अंतिम निर्णय दाखवते, प्रत्येक निर्णय नाही.`,
  rlBombaySample: (p, w) =>
    `गेल्या ${w} आठवड्यांतील प्रत्येक आठवड्याचे ${p} सर्वात अलीकडील अंतिम आदेश आणि निर्णय दाखवते, नेहमीचे 'disposed off' आदेश वगळून. काही आठवड्यांत कमी किंवा कोणतीही नोंद नाही, म्हणून ही पूर्ण यादी नाही. संग्रह पूर्ण निर्णय आणि लहान आदेश यांत फरक करत नाही.`,
  rlAttribution:
    "तारखा संग्रहात नोंदवल्याप्रमाणे आहेत आणि त्यात चुका असू शकतात. फौजदारी आणि दिवाणी लेबले प्रकरणाच्या प्रकारावरून काढलेली आहेत आणि अचूक नसू शकतात. संग्रह CC BY 4.0 आहेत, Dattam Labs आणि डेटासेट सांभाळणाऱ्यांकडून. न्यायालयाची स्वतःची प्रत तपासा.",
  rlCaseType: "प्रकरणाचा प्रकार",
  rlCaseNumber: "प्रकरण क्रमांक",
  rlBenchCol: "खंडपीठ",
  rlDecided: "निर्णयाची तारीख",
  rlOutcome: "निकाल",
  rlLoading: "निर्णय लोड होत आहेत…",
  rlFailed: "संग्रह लोड होऊ शकला नाही. सेवा चालू आहे का ते तपासा, मग पुन्हा प्रयत्न करा.",
  linkOther: (site) => `प्रत वाचा (${site})`,
  dateToVerify: "तारीख तपासायची आहे",

  stTitle: "सेटिंग्ज",
  stLede: "तुमचे खाते आणि LawShift तुम्हाला कसे उत्तर देते.",
  stEmailTitle: "ईमेल",
  stEmailNote: "हा तुमच्या खात्याचा पत्ता आहे. तो येथे बदलता येत नाही.",
  stLangTitle: "उत्तराची डीफॉल्ट भाषा",
  stLangNote: "उत्तरे इंग्रजीत लिहिली जातात आणि कायदेशीर काम झाल्यानंतर मशीन-भाषांतरित होतात.",
  stPasswordTitle: "पासवर्ड बदला",
  stCurrent: "सध्याचा पासवर्ड",
  stNew: "नवीन पासवर्ड",
  stConfirm: "नवीन पासवर्डची पुष्टी करा",
  stUpdate: "पासवर्ड अपडेट करा",
  stUpdating: "अपडेट होत आहे…",
  stUpdated: "पासवर्ड अपडेट झाला.",
  stDeleteTitle: "खाते हटवा",
  stDeleteBody:
    "यामुळे तुमचे खाते, जतन केलेला प्रकरण इतिहास आणि जतन केलेले दस्तऐवज (फाइल्स आणि तुमची वर्णने) हटतील. हे परत करता येणार नाही.",
  stDeleteType: (e) => `पुष्टीसाठी ${e} लिहा`,
  stDeleteButton: "खाते हटवा",
  stDeleteDone:
    "पूर्वावलोकन: लाइव्ह आवृत्तीत तुमचे खाते, प्रकरण इतिहास आणि साठवलेले दस्तऐवज आता हटवले गेले असते.",
};

const DICTS: Record<Lang, DashboardCopy> = { en, hi, mr };

export function getDashboardCopy(lang: Lang): DashboardCopy {
  return DICTS[lang] ?? en;
}
