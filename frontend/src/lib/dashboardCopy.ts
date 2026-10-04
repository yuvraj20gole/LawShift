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

  previewNote: string;
  previewShow: string;
  previewSample: string;
  previewEmpty: string;
  tagSample: string;
  tagReal: string;

  describeCase: string;
  open: string;
  verOk: string;
  verFlag: string;
  codeIpc: string;
  codeBns: string;

  wsTitle: string;
  wsLede: string;
  atTitle: string;
  atFrom: string;
  atUpload: string;
  atPickLabel: string;
  atNoDocs: string;
  atWord: string;
  atChip: string;
  atRemove: string;
  atDateFound: (d: string) => string;
  atDateNone: string;
  atEdit: string;
  atConfirm: string;
  atSave: string;
  atDateLabel: string;
  atConfirmed: (d: string) => string;
  atChange: string;
  atScanNote: string;
  atPreview: string;

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

  dcTitle: string;
  dcLede: string;
  dzTitle: string;
  dzChoose: string;
  dzTypes: string;
  dzTypesWord: string;
  dzOcr: string;
  dzBad: string;
  dzWord: string;
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

  soonTag: string;
  soonNothing: string;
  soonBack: string;
  mapTitle: string;
  mapWill: string;
  rulTitle: string;
  rulWill: string;

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

  previewNote: "Preview: sample data, nothing is saved.",
  previewShow: "Show",
  previewSample: "Sample data",
  previewEmpty: "Empty account",
  tagSample: "Sample data",
  tagReal: "Real archive data",

  describeCase: "Describe a case",
  open: "Open",
  verOk: "No inconsistency detected",
  verFlag: "Worth double-checking",
  codeIpc: "IPC",
  codeBns: "BNS",

  wsTitle: "Workspace",
  wsLede: "Describe what happened and when. Answers come from the statute text.",
  atTitle: "Attach a document",
  atFrom: "From your documents",
  atUpload: "Upload new",
  atPickLabel: "Choose a document",
  atNoDocs: "You have no stored documents yet. Use Upload new.",
  atWord: "Word (.docx) is not connected yet in this preview.",
  atChip: "Attached",
  atRemove: "Remove",
  atDateFound: (d) => `Date found: ${d}, read from the document`,
  atDateNone: "No date found yet. Enter the offence date from the document.",
  atEdit: "Edit",
  atConfirm: "Confirm date",
  atSave: "Save date",
  atDateLabel: "Offence date",
  atConfirmed: (d) => `Offence date confirmed: ${d}. Follow-up questions in this conversation use it.`,
  atChange: "Change",
  atScanNote: "Scanned documents can misread dates and digits. Confirm the date before you ask.",
  atPreview: "Preview: attaching a document doesn't change what the chat sends yet.",

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

  dcTitle: "Documents",
  dcLede: "Add a document and LawShift reads the facts and the date from it.",
  dzTitle: "Drop a file here, or",
  dzChoose: "choose a file",
  dzTypes: "PDF, JPG or PNG",
  dzTypesWord: "PDF, JPG, PNG or DOCX (Word is not connected yet)",
  dzOcr:
    "Typed PDFs are read directly. Scanned documents and photos are read with OCR, which can misread dates and digits, so check the date it found.",
  dzBad: "That file type isn't supported. Use a PDF, JPG or PNG.",
  dzWord: "Word (.docx) isn't connected yet in this preview. Use a PDF, JPG or PNG.",
  dcListTitle: "Uploaded documents",
  colFile: "File",
  colDate: "Added",
  colRead: "How it was read",
  colResult: "Result",
  readDirect: "Typed PDF, read directly",
  readOcr: "Read with OCR",
  readPending: "Not processed (preview)",
  viewResult: "View result",
  dcEmptyTitle: "No documents yet",
  dcEmptyBody: "Files you add will be listed here with how their text was read.",

  soonTag: "Coming next",
  soonNothing: "Nothing is listed here yet, because this page isn't built.",
  soonBack: "Back to Workspace",
  mapTitle: "Mapping",
  mapWill:
    "This page will show how an IPC section maps to its BNS section: whether the match is one-to-one, partial, merged or dropped, with both texts side by side, from the IPC–BNS mapping table.",
  rulTitle: "Rulings",
  rulWill:
    "This page will list court judgments from the archive, which you can filter by court and by criminal or civil, plus a Background group of judgments on which code applies. Background entries stay marked as drafts until they have been checked.",

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
    "This deletes your account, your case history and every document you have stored with us. It can't be undone.",
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

  previewNote: "पूर्वावलोकन: नमूना डेटा, कुछ भी सहेजा नहीं जाता।",
  previewShow: "दिखाएँ",
  previewSample: "नमूना डेटा",
  previewEmpty: "खाली खाता",
  tagSample: "नमूना डेटा",
  tagReal: "असली अभिलेखागार डेटा",

  describeCase: "एक केस बताएँ",
  open: "खोलें",
  verOk: "कोई असंगति नहीं मिली",
  verFlag: "दोबारा जाँचने योग्य",
  codeIpc: "IPC",
  codeBns: "BNS",

  wsTitle: "कार्यक्षेत्र",
  wsLede: "बताएँ कि क्या हुआ और कब। उत्तर वैधानिक पाठ से आते हैं।",
  atTitle: "दस्तावेज़ संलग्न करें",
  atFrom: "आपके दस्तावेज़ों से",
  atUpload: "नया अपलोड करें",
  atPickLabel: "दस्तावेज़ चुनें",
  atNoDocs: "अभी आपके कोई सहेजे दस्तावेज़ नहीं हैं। नया अपलोड करें का उपयोग करें।",
  atWord: "इस पूर्वावलोकन में Word (.docx) अभी जुड़ा नहीं है।",
  atChip: "संलग्न",
  atRemove: "हटाएँ",
  atDateFound: (d) => `मिली तिथि: ${d}, दस्तावेज़ से पढ़ी गई`,
  atDateNone: "अभी कोई तिथि नहीं मिली। दस्तावेज़ से अपराध की तिथि लिखें।",
  atEdit: "बदलें",
  atConfirm: "तिथि की पुष्टि करें",
  atSave: "तिथि सहेजें",
  atDateLabel: "अपराध की तिथि",
  atConfirmed: (d) => `अपराध की तिथि की पुष्टि हुई: ${d}। इस बातचीत के आगे के प्रश्न इसी का उपयोग करेंगे।`,
  atChange: "बदलें",
  atScanNote: "स्कैन किए दस्तावेज़ तिथियाँ और अंक गलत पढ़ सकते हैं। पूछने से पहले तिथि की पुष्टि करें।",
  atPreview: "पूर्वावलोकन: दस्तावेज़ संलग्न करने से अभी चैट जो भेजती है वह नहीं बदलता।",

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

  dcTitle: "दस्तावेज़",
  dcLede: "दस्तावेज़ जोड़ें, LawShift उससे तथ्य और तिथि पढ़ लेगा।",
  dzTitle: "फ़ाइल यहाँ छोड़ें, या",
  dzChoose: "फ़ाइल चुनें",
  dzTypes: "PDF, JPG या PNG",
  dzTypesWord: "PDF, JPG, PNG या DOCX (Word अभी जुड़ा नहीं है)",
  dzOcr:
    "टाइप किए PDF सीधे पढ़े जाते हैं। स्कैन किए दस्तावेज़ और फ़ोटो OCR से पढ़े जाते हैं, जो तिथियाँ और अंक गलत पढ़ सकता है, इसलिए मिली तिथि जाँच लें।",
  dzBad: "यह फ़ाइल प्रकार समर्थित नहीं है। PDF, JPG या PNG का उपयोग करें।",
  dzWord: "इस पूर्वावलोकन में Word (.docx) अभी जुड़ा नहीं है। PDF, JPG या PNG का उपयोग करें।",
  dcListTitle: "अपलोड किए दस्तावेज़",
  colFile: "फ़ाइल",
  colDate: "जोड़ा गया",
  colRead: "कैसे पढ़ा गया",
  colResult: "परिणाम",
  readDirect: "टाइप किया PDF, सीधे पढ़ा गया",
  readOcr: "OCR से पढ़ा गया",
  readPending: "संसाधित नहीं (पूर्वावलोकन)",
  viewResult: "परिणाम देखें",
  dcEmptyTitle: "अभी कोई दस्तावेज़ नहीं",
  dcEmptyBody: "आपके जोड़े फ़ाइलें यहाँ दिखेंगी, साथ में कि उनका पाठ कैसे पढ़ा गया।",

  soonTag: "आगे आ रहा है",
  soonNothing: "यहाँ अभी कुछ सूचीबद्ध नहीं है, क्योंकि यह पृष्ठ बना नहीं है।",
  soonBack: "कार्यक्षेत्र पर वापस जाएँ",
  mapTitle: "मैपिंग",
  mapWill:
    "यह पृष्ठ दिखाएगा कि IPC की कोई धारा BNS की किस धारा से मेल खाती है: मिलान एक-से-एक है, आंशिक, मिला हुआ या हटा हुआ, दोनों पाठ साथ-साथ, IPC–BNS मैपिंग तालिका से।",
  rulTitle: "निर्णय",
  rulWill:
    "यह पृष्ठ अभिलेखागार से न्यायालयों के निर्णय सूचीबद्ध करेगा, जिन्हें आप न्यायालय और आपराधिक या दीवानी के आधार पर छान सकेंगे, साथ में एक पृष्ठभूमि समूह उन निर्णयों का जो बताते हैं कि कौन-सी संहिता लागू होती है। पृष्ठभूमि प्रविष्टियाँ जाँचे जाने तक मसौदा चिह्नित रहेंगी।",

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
    "इससे आपका खाता, केस इतिहास और हमारे पास सहेजे आपके सभी दस्तावेज़ हट जाएँगे। इसे वापस नहीं किया जा सकता।",
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

  previewNote: "पूर्वावलोकन: नमुना डेटा, काहीही जतन केले जात नाही.",
  previewShow: "दाखवा",
  previewSample: "नमुना डेटा",
  previewEmpty: "रिकामे खाते",
  tagSample: "नमुना डेटा",
  tagReal: "खरा संग्रह डेटा",

  describeCase: "एक प्रकरण सांगा",
  open: "उघडा",
  verOk: "कोणतीही विसंगती आढळली नाही",
  verFlag: "पुन्हा तपासण्यासारखे",
  codeIpc: "IPC",
  codeBns: "BNS",

  wsTitle: "कार्यक्षेत्र",
  wsLede: "काय घडले आणि कधी ते सांगा. उत्तरे वैधानिक मजकुरातून येतात.",
  atTitle: "दस्तऐवज जोडा",
  atFrom: "तुमच्या दस्तऐवजांतून",
  atUpload: "नवीन अपलोड करा",
  atPickLabel: "दस्तऐवज निवडा",
  atNoDocs: "अजून तुमचे कोणतेही जतन केलेले दस्तऐवज नाहीत. नवीन अपलोड करा वापरा.",
  atWord: "या पूर्वावलोकनात Word (.docx) अजून जोडलेले नाही.",
  atChip: "जोडले",
  atRemove: "काढा",
  atDateFound: (d) => `सापडलेली तारीख: ${d}, दस्तऐवजातून वाचलेली`,
  atDateNone: "अजून तारीख सापडली नाही. दस्तऐवजातून गुन्ह्याची तारीख लिहा.",
  atEdit: "बदला",
  atConfirm: "तारखेची पुष्टी करा",
  atSave: "तारीख जतन करा",
  atDateLabel: "गुन्ह्याची तारीख",
  atConfirmed: (d) => `गुन्ह्याच्या तारखेची पुष्टी झाली: ${d}. या संभाषणातील पुढचे प्रश्न तीच वापरतील.`,
  atChange: "बदला",
  atScanNote: "स्कॅन केलेले दस्तऐवज तारखा आणि अंक चुकीचे वाचू शकतात. विचारण्यापूर्वी तारखेची पुष्टी करा.",
  atPreview: "पूर्वावलोकन: दस्तऐवज जोडल्याने चॅट जे पाठवते ते अजून बदलत नाही.",

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

  dcTitle: "दस्तऐवज",
  dcLede: "दस्तऐवज जोडा, LawShift त्यातून तथ्ये आणि तारीख वाचेल.",
  dzTitle: "फाइल येथे सोडा, किंवा",
  dzChoose: "फाइल निवडा",
  dzTypes: "PDF, JPG किंवा PNG",
  dzTypesWord: "PDF, JPG, PNG किंवा DOCX (Word अजून जोडलेले नाही)",
  dzOcr:
    "टाइप केलेले PDF थेट वाचले जातात. स्कॅन केलेले दस्तऐवज आणि फोटो OCR ने वाचले जातात, जे तारखा आणि अंक चुकीचे वाचू शकते, म्हणून सापडलेली तारीख तपासा.",
  dzBad: "हा फाइल प्रकार समर्थित नाही. PDF, JPG किंवा PNG वापरा.",
  dzWord: "या पूर्वावलोकनात Word (.docx) अजून जोडलेले नाही. PDF, JPG किंवा PNG वापरा.",
  dcListTitle: "अपलोड केलेले दस्तऐवज",
  colFile: "फाइल",
  colDate: "जोडले",
  colRead: "कसे वाचले",
  colResult: "निकाल",
  readDirect: "टाइप केलेले PDF, थेट वाचले",
  readOcr: "OCR ने वाचले",
  readPending: "प्रक्रिया नाही (पूर्वावलोकन)",
  viewResult: "निकाल पाहा",
  dcEmptyTitle: "अजून कोणतेही दस्तऐवज नाहीत",
  dcEmptyBody: "तुम्ही जोडलेल्या फाइल्स येथे दिसतील, त्यांचा मजकूर कसा वाचला गेला यासह.",

  soonTag: "पुढे येत आहे",
  soonNothing: "येथे अजून काहीही यादीत नाही, कारण हे पान तयार झालेले नाही.",
  soonBack: "कार्यक्षेत्राकडे परत जा",
  mapTitle: "मॅपिंग",
  mapWill:
    "हे पान दाखवेल की IPC चे एखादे कलम BNS च्या कोणत्या कलमाशी जुळते: जुळणी एक-ते-एक आहे, आंशिक, एकत्रित की वगळलेली, दोन्ही मजकूर शेजारी-शेजारी, IPC–BNS मॅपिंग तक्त्यातून.",
  rulTitle: "निर्णय",
  rulWill:
    "हे पान संग्रहातील न्यायालयांचे निर्णय यादीत देईल, जे तुम्ही न्यायालय आणि फौजदारी किंवा दिवाणी नुसार गाळू शकाल, तसेच कोणती संहिता लागू होते यावरील निर्णयांचा एक पार्श्वभूमी गट. पार्श्वभूमी नोंदी तपासल्या जाईपर्यंत मसुदा म्हणून चिन्हांकित राहतील.",

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
    "यामुळे तुमचे खाते, प्रकरण इतिहास आणि आमच्याकडे साठवलेले तुमचे सर्व दस्तऐवज हटतील. हे परत करता येणार नाही.",
  stDeleteType: (e) => `पुष्टीसाठी ${e} लिहा`,
  stDeleteButton: "खाते हटवा",
  stDeleteDone:
    "पूर्वावलोकन: लाइव्ह आवृत्तीत तुमचे खाते, प्रकरण इतिहास आणि साठवलेले दस्तऐवज आता हटवले गेले असते.",
};

const DICTS: Record<Lang, DashboardCopy> = { en, hi, mr };

export function getDashboardCopy(lang: Lang): DashboardCopy {
  return DICTS[lang] ?? en;
}
