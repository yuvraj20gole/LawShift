import type { Lang } from "./prefs";

/** Copy for the account area (EN / HI / MR). Hindi and Marathi need native review. */
export type DashboardCopy = {
  navLabel: string;
  menu: string;
  navOverview: string;
  navWorkspace: string;
  navHistory: string;
  navSaved: string;
  navDocuments: string;
  navSettings: string;
  headerDashboard: string;
  logout: string;

  previewNote: string;
  previewShow: string;
  previewSample: string;
  previewEmpty: string;

  describeCase: string;
  open: string;
  remove: string;
  keep: string;
  verOk: string;
  verFlag: string;
  codeIpc: string;
  codeBns: string;

  ovTitle: string;
  ovWelcome: string;
  ovQuestionsTitle: string;
  ovQuestionsLeft: (n: number, total: number) => string;
  ovQuestionsNote: string;
  ovRecentTitle: string;
  ovRecentLede: string;
  ovAllCases: string;
  ovEmptyTitle: string;
  ovEmptyBody: string;

  wsTitle: string;
  wsLede: string;
  wsUploadTitle: string;
  wsUploadNote: string;

  hiTitle: string;
  hiLede: string;
  hiSearch: string;
  hiSearchHint: string;
  hiFilter: string;
  fAll: string;
  fIpc: string;
  fBns: string;
  colAsked: string;
  colOffence: string;
  colCode: string;
  colSection: string;
  colState: string;
  colAction: string;
  hiCount: (n: number) => string;
  hiEmptyTitle: string;
  hiEmptyBody: string;
  hiNoMatchTitle: string;
  hiNoMatchBody: string;
  clearFilters: string;

  svTitle: string;
  svLede: string;
  svSaved: (d: string) => string;
  svRemoveAsk: (label: string) => string;
  svRemoveBody: string;
  svEmptyTitle: string;
  svEmptyBody: string;

  dcTitle: string;
  dcLede: string;
  dzTitle: string;
  dzChoose: string;
  dzTypes: string;
  dzOcr: string;
  dzBad: string;
  dcListTitle: string;
  colFile: string;
  colDate: string;
  colRead: string;
  colResult: string;
  readDirect: string;
  readOcr: string;
  readPending: string;
  viewResult: string;
  dcEmptyTitle: string;
  dcEmptyBody: string;

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
  navOverview: "Overview",
  navWorkspace: "Workspace",
  navHistory: "Case history",
  navSaved: "Saved sections",
  navDocuments: "Documents",
  navSettings: "Settings",
  headerDashboard: "Dashboard",
  logout: "Log out",

  previewNote: "Preview: sample data, nothing is saved.",
  previewShow: "Show",
  previewSample: "Sample data",
  previewEmpty: "Empty account",

  describeCase: "Describe a case",
  open: "Open",
  remove: "Remove",
  keep: "Keep it",
  verOk: "No inconsistency detected",
  verFlag: "Worth double-checking",
  codeIpc: "IPC",
  codeBns: "BNS",

  ovTitle: "Overview",
  ovWelcome: "Welcome back.",
  ovQuestionsTitle: "Questions left",
  ovQuestionsLeft: (n, t) => `${n} of ${t} questions left`,
  ovQuestionsNote: "Sample figure. In the live version the count comes from your account.",
  ovRecentTitle: "Recent cases",
  ovRecentLede: "Your last five questions.",
  ovAllCases: "See all cases",
  ovEmptyTitle: "No cases yet",
  ovEmptyBody: "Describe what happened and when. Your questions will be listed here.",

  wsTitle: "Workspace",
  wsLede: "Describe what happened and when. Answers come from the statute text.",
  wsUploadTitle: "Upload a document",
  wsUploadNote:
    "Upload will sit here once it is connected to the chat. For now it only previews how a document is added.",

  hiTitle: "Case history",
  hiLede: "Every question you have asked, with the code it was routed to.",
  hiSearch: "Search cases",
  hiSearchHint: "Search by section, title or question",
  hiFilter: "Code",
  fAll: "All",
  fIpc: "IPC",
  fBns: "BNS",
  colAsked: "Asked",
  colOffence: "Offence date",
  colCode: "Code",
  colSection: "Section",
  colState: "Check",
  colAction: "Action",
  hiCount: (n) => `${n} ${n === 1 ? "case" : "cases"}`,
  hiEmptyTitle: "No cases yet",
  hiEmptyBody: "Questions you ask in the workspace will be listed here with their section and check result.",
  hiNoMatchTitle: "No cases match",
  hiNoMatchBody: "Try a different word, or show both codes.",
  clearFilters: "Clear search and filter",

  svTitle: "Saved sections",
  svLede: "Sections you have kept for later.",
  svSaved: (d) => `Saved ${d}`,
  svRemoveAsk: (l) => `Remove ${l} from saved sections?`,
  svRemoveBody: "This only removes your bookmark. The statute itself is unchanged.",
  svEmptyTitle: "Nothing saved yet",
  svEmptyBody: "Save a section from an answer and it will be kept here.",

  dcTitle: "Documents",
  dcLede: "Add a document and LawShift reads the facts and the date from it.",
  dzTitle: "Drop a file here, or",
  dzChoose: "choose a file",
  dzTypes: "PDF, JPG or PNG",
  dzOcr:
    "Typed PDFs are read directly. Scanned documents and photos are read with OCR, which can misread dates and digits, so check the date it found.",
  dzBad: "That file type isn't supported. Use a PDF, JPG or PNG.",
  dcListTitle: "Uploaded documents",
  colFile: "File",
  colDate: "Added",
  colRead: "How it was read",
  colResult: "Result",
  readDirect: "Read directly",
  readOcr: "Read with OCR",
  readPending: "Not processed (preview)",
  viewResult: "View result",
  dcEmptyTitle: "No documents yet",
  dcEmptyBody: "Files you add will be listed here with how their text was read.",

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
  stUpdated: "Password updated (placeholder: nothing was changed).",
  stDeleteTitle: "Delete account",
  stDeleteBody:
    "This removes your account, your case history, saved sections and documents. It can't be undone.",
  stDeleteType: (e) => `Type ${e} to confirm`,
  stDeleteButton: "Delete account",
  stDeleteDone:
    "Preview: in the live version your account and everything in it would be deleted now.",
};

const hi: DashboardCopy = {
  navLabel: "खाता",
  menu: "मेनू",
  navOverview: "अवलोकन",
  navWorkspace: "कार्यक्षेत्र",
  navHistory: "केस इतिहास",
  navSaved: "सहेजी गई धाराएँ",
  navDocuments: "दस्तावेज़",
  navSettings: "सेटिंग्स",
  headerDashboard: "डैशबोर्ड",
  logout: "लॉग आउट",

  previewNote: "पूर्वावलोकन: नमूना डेटा, कुछ भी सहेजा नहीं जाता।",
  previewShow: "दिखाएँ",
  previewSample: "नमूना डेटा",
  previewEmpty: "खाली खाता",

  describeCase: "एक केस बताएँ",
  open: "खोलें",
  remove: "हटाएँ",
  keep: "रहने दें",
  verOk: "कोई असंगति नहीं मिली",
  verFlag: "दोबारा जाँचने योग्य",
  codeIpc: "IPC",
  codeBns: "BNS",

  ovTitle: "अवलोकन",
  ovWelcome: "वापसी पर स्वागत है।",
  ovQuestionsTitle: "बचे हुए प्रश्न",
  ovQuestionsLeft: (n, t) => `${t} में से ${n} प्रश्न शेष`,
  ovQuestionsNote: "नमूना आँकड़ा। लाइव संस्करण में गिनती आपके खाते से आएगी।",
  ovRecentTitle: "हाल के केस",
  ovRecentLede: "आपके पिछले पाँच प्रश्न।",
  ovAllCases: "सभी केस देखें",
  ovEmptyTitle: "अभी कोई केस नहीं",
  ovEmptyBody: "बताएँ कि क्या हुआ और कब। आपके प्रश्न यहाँ सूचीबद्ध होंगे।",

  wsTitle: "कार्यक्षेत्र",
  wsLede: "बताएँ कि क्या हुआ और कब। उत्तर वैधानिक पाठ से आते हैं।",
  wsUploadTitle: "दस्तावेज़ अपलोड करें",
  wsUploadNote:
    "चैट से जुड़ने के बाद अपलोड यहाँ रहेगा। अभी यह केवल दिखाता है कि दस्तावेज़ कैसे जोड़ा जाता है।",

  hiTitle: "केस इतिहास",
  hiLede: "आपके पूछे हर प्रश्न, और जिस संहिता में वह गया।",
  hiSearch: "केस खोजें",
  hiSearchHint: "धारा, शीर्षक या प्रश्न से खोजें",
  hiFilter: "संहिता",
  fAll: "सभी",
  fIpc: "IPC",
  fBns: "BNS",
  colAsked: "पूछा गया",
  colOffence: "अपराध की तिथि",
  colCode: "संहिता",
  colSection: "धारा",
  colState: "जाँच",
  colAction: "कार्रवाई",
  hiCount: (n) => `${n} केस`,
  hiEmptyTitle: "अभी कोई केस नहीं",
  hiEmptyBody: "कार्यक्षेत्र में आपके पूछे प्रश्न धारा और जाँच परिणाम के साथ यहाँ दिखेंगे।",
  hiNoMatchTitle: "कोई केस मेल नहीं खाता",
  hiNoMatchBody: "कोई दूसरा शब्द आज़माएँ, या दोनों संहिताएँ दिखाएँ।",
  clearFilters: "खोज और फ़िल्टर हटाएँ",

  svTitle: "सहेजी गई धाराएँ",
  svLede: "वे धाराएँ जो आपने बाद के लिए रखी हैं।",
  svSaved: (d) => `सहेजी: ${d}`,
  svRemoveAsk: (l) => `क्या ${l} को सहेजी गई धाराओं से हटाएँ?`,
  svRemoveBody: "इससे केवल आपका बुकमार्क हटेगा। वैधानिक पाठ वैसा ही रहेगा।",
  svEmptyTitle: "अभी कुछ सहेजा नहीं गया",
  svEmptyBody: "किसी उत्तर से धारा सहेजें, वह यहाँ रखी जाएगी।",

  dcTitle: "दस्तावेज़",
  dcLede: "दस्तावेज़ जोड़ें, LawShift उससे तथ्य और तिथि पढ़ लेगा।",
  dzTitle: "फ़ाइल यहाँ छोड़ें, या",
  dzChoose: "फ़ाइल चुनें",
  dzTypes: "PDF, JPG या PNG",
  dzOcr:
    "टाइप किए PDF सीधे पढ़े जाते हैं। स्कैन किए दस्तावेज़ और फ़ोटो OCR से पढ़े जाते हैं, जो तिथियाँ और अंक गलत पढ़ सकता है, इसलिए मिली तिथि जाँच लें।",
  dzBad: "यह फ़ाइल प्रकार समर्थित नहीं है। PDF, JPG या PNG का उपयोग करें।",
  dcListTitle: "अपलोड किए दस्तावेज़",
  colFile: "फ़ाइल",
  colDate: "जोड़ा गया",
  colRead: "कैसे पढ़ा गया",
  colResult: "परिणाम",
  readDirect: "सीधे पढ़ा गया",
  readOcr: "OCR से पढ़ा गया",
  readPending: "संसाधित नहीं (पूर्वावलोकन)",
  viewResult: "परिणाम देखें",
  dcEmptyTitle: "अभी कोई दस्तावेज़ नहीं",
  dcEmptyBody: "आपके जोड़े फ़ाइलें यहाँ दिखेंगी, साथ में कि उनका पाठ कैसे पढ़ा गया।",

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
  stUpdated: "पासवर्ड अपडेट हुआ (प्लेसहोल्डर: कुछ नहीं बदला)।",
  stDeleteTitle: "खाता हटाएँ",
  stDeleteBody:
    "इससे आपका खाता, केस इतिहास, सहेजी धाराएँ और दस्तावेज़ हट जाएँगे। इसे वापस नहीं किया जा सकता।",
  stDeleteType: (e) => `पुष्टि के लिए ${e} लिखें`,
  stDeleteButton: "खाता हटाएँ",
  stDeleteDone:
    "पूर्वावलोकन: लाइव संस्करण में आपका खाता और उसमें सब कुछ अभी हटा दिया जाता।",
};

const mr: DashboardCopy = {
  navLabel: "खाते",
  menu: "मेनू",
  navOverview: "आढावा",
  navWorkspace: "कार्यक्षेत्र",
  navHistory: "प्रकरण इतिहास",
  navSaved: "जतन केलेली कलमे",
  navDocuments: "दस्तऐवज",
  navSettings: "सेटिंग्ज",
  headerDashboard: "डॅशबोर्ड",
  logout: "लॉग आउट",

  previewNote: "पूर्वावलोकन: नमुना डेटा, काहीही जतन केले जात नाही.",
  previewShow: "दाखवा",
  previewSample: "नमुना डेटा",
  previewEmpty: "रिकामे खाते",

  describeCase: "एक प्रकरण सांगा",
  open: "उघडा",
  remove: "काढा",
  keep: "ठेवा",
  verOk: "कोणतीही विसंगती आढळली नाही",
  verFlag: "पुन्हा तपासण्यासारखे",
  codeIpc: "IPC",
  codeBns: "BNS",

  ovTitle: "आढावा",
  ovWelcome: "पुन्हा स्वागत आहे.",
  ovQuestionsTitle: "उरलेले प्रश्न",
  ovQuestionsLeft: (n, t) => `${t} पैकी ${n} प्रश्न शिल्लक`,
  ovQuestionsNote: "नमुना आकडा. लाइव्ह आवृत्तीत ही गणना तुमच्या खात्यातून येईल.",
  ovRecentTitle: "अलीकडील प्रकरणे",
  ovRecentLede: "तुमचे शेवटचे पाच प्रश्न.",
  ovAllCases: "सर्व प्रकरणे पाहा",
  ovEmptyTitle: "अजून कोणतेही प्रकरण नाही",
  ovEmptyBody: "काय घडले आणि कधी ते सांगा. तुमचे प्रश्न येथे यादीत दिसतील.",

  wsTitle: "कार्यक्षेत्र",
  wsLede: "काय घडले आणि कधी ते सांगा. उत्तरे वैधानिक मजकुरातून येतात.",
  wsUploadTitle: "दस्तऐवज अपलोड करा",
  wsUploadNote:
    "चॅटशी जोडल्यानंतर अपलोड येथे असेल. सध्या ते फक्त दस्तऐवज कसा जोडला जातो ते दाखवते.",

  hiTitle: "प्रकरण इतिहास",
  hiLede: "तुम्ही विचारलेले प्रत्येक प्रश्न, आणि तो ज्या संहितेकडे गेला.",
  hiSearch: "प्रकरणे शोधा",
  hiSearchHint: "कलम, शीर्षक किंवा प्रश्नाने शोधा",
  hiFilter: "संहिता",
  fAll: "सर्व",
  fIpc: "IPC",
  fBns: "BNS",
  colAsked: "विचारले",
  colOffence: "गुन्ह्याची तारीख",
  colCode: "संहिता",
  colSection: "कलम",
  colState: "तपासणी",
  colAction: "कृती",
  hiCount: (n) => `${n} प्रकरणे`,
  hiEmptyTitle: "अजून कोणतेही प्रकरण नाही",
  hiEmptyBody: "कार्यक्षेत्रात तुम्ही विचारलेले प्रश्न कलम आणि तपासणी निकालासह येथे दिसतील.",
  hiNoMatchTitle: "कोणतेही प्रकरण जुळत नाही",
  hiNoMatchBody: "वेगळा शब्द वापरून पाहा, किंवा दोन्ही संहिता दाखवा.",
  clearFilters: "शोध आणि फिल्टर काढा",

  svTitle: "जतन केलेली कलमे",
  svLede: "नंतरसाठी ठेवलेली कलमे.",
  svSaved: (d) => `जतन केले: ${d}`,
  svRemoveAsk: (l) => `${l} जतन केलेल्या कलमांतून काढायचे?`,
  svRemoveBody: "यामुळे फक्त तुमचा बुकमार्क निघेल. वैधानिक मजकूर तसाच राहील.",
  svEmptyTitle: "अजून काहीही जतन केलेले नाही",
  svEmptyBody: "उत्तरातून कलम जतन करा, ते येथे ठेवले जाईल.",

  dcTitle: "दस्तऐवज",
  dcLede: "दस्तऐवज जोडा, LawShift त्यातून तथ्ये आणि तारीख वाचेल.",
  dzTitle: "फाइल येथे सोडा, किंवा",
  dzChoose: "फाइल निवडा",
  dzTypes: "PDF, JPG किंवा PNG",
  dzOcr:
    "टाइप केलेले PDF थेट वाचले जातात. स्कॅन केलेले दस्तऐवज आणि फोटो OCR ने वाचले जातात, जे तारखा आणि अंक चुकीचे वाचू शकते, म्हणून सापडलेली तारीख तपासा.",
  dzBad: "हा फाइल प्रकार समर्थित नाही. PDF, JPG किंवा PNG वापरा.",
  dcListTitle: "अपलोड केलेले दस्तऐवज",
  colFile: "फाइल",
  colDate: "जोडले",
  colRead: "कसे वाचले",
  colResult: "निकाल",
  readDirect: "थेट वाचले",
  readOcr: "OCR ने वाचले",
  readPending: "प्रक्रिया नाही (पूर्वावलोकन)",
  viewResult: "निकाल पाहा",
  dcEmptyTitle: "अजून कोणतेही दस्तऐवज नाहीत",
  dcEmptyBody: "तुम्ही जोडलेल्या फाइल्स येथे दिसतील, त्यांचा मजकूर कसा वाचला गेला यासह.",

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
  stUpdated: "पासवर्ड अपडेट झाला (प्लेसहोल्डर: काहीही बदलले नाही).",
  stDeleteTitle: "खाते हटवा",
  stDeleteBody:
    "यामुळे तुमचे खाते, प्रकरण इतिहास, जतन केलेली कलमे आणि दस्तऐवज हटतील. हे परत करता येणार नाही.",
  stDeleteType: (e) => `पुष्टीसाठी ${e} लिहा`,
  stDeleteButton: "खाते हटवा",
  stDeleteDone:
    "पूर्वावलोकन: लाइव्ह आवृत्तीत तुमचे खाते आणि त्यातील सर्व काही आता हटवले गेले असते.",
};

const DICTS: Record<Lang, DashboardCopy> = { en, hi, mr };

export function getDashboardCopy(lang: Lang): DashboardCopy {
  return DICTS[lang] ?? en;
}
