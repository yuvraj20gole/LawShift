import type { Lang } from "@/lib/prefs";

/**
 * Copy for stored documents: the Documents page, the review step and the
 * Workspace attach control. Hindi and Marathi are agent drafts and need
 * native review before launch.
 */
export type DocCopy = {
  // review step
  rvTitle: string;
  rvFile: string;
  rvHow: string;
  readTyped: string;
  readOcr: string;
  readDocx: string;
  wOcr: string;
  wNoText: string;
  wTruncated: string;
  wMultiple: string;
  wPages: string;
  wPassword: string;
  dateTitle: string;
  dateNone: string;
  dateManualOption: string;
  dateInputLabel: string;
  dateConfirm: string;
  dateEditedNote: string;
  descTitle: string;
  descHelp: string;
  descCount: (n: number, max: number) => string;
  descShort: string;
  textReadTitle: string;
  textReadNote: string;
  needConfirm: string;
  // dropzone
  dzTitle: string;
  dzChoose: string;
  dzTypes: string;
  dzBadType: string;
  reading: string;
  // documents page
  dcLede: string;
  dcStoreNote: string;
  dcUploadTitle: string;
  dcListTitle: string;
  colFile: string;
  colSaved: string;
  colRead: string;
  colDate: string;
  colSize: string;
  colActions: string;
  useInWorkspace: string;
  download: string;
  del: string;
  delAll: string;
  delTitle: string;
  delBody: string;
  delConfirm: string;
  delAllTitle: (n: number) => string;
  delAllBody: string;
  delAllConfirm: string;
  cancel: string;
  save: string;
  saving: string;
  saved: string;
  discard: string;
  loading: string;
  loadError: string;
  retry: string;
  emptyTitle: string;
  emptyBody: string;
  // workspace
  wsAttachTitle: string;
  wsFrom: string;
  wsUpload: string;
  wsPick: string;
  wsNone: string;
  wsAttachOnly: string;
  wsSaveAttach: string;
  wsAttachStored: string;
  wsWorking: string;
  wsChip: string;
  wsThisChatOnly: string;
  wsSavedDoc: string;
  wsChangeDate: string;
  wsRemove: string;
  wsAfter: string;
  wsCancel: string;
  // settings
  stFilesFailed: string;
  // errors
  err401: string;
  err413: string;
  err415: string;
  err422: string;
  err429: string;
  err503: string;
  errNetwork: string;
  errGeneric: string;
  errSave: string;
  errDelete: string;
  errDownload: string;
  errAttach: string;
  errDetach: string;
};

const en: DocCopy = {
  rvTitle: "Check what was read",
  rvFile: "File",
  rvHow: "How it was read",
  readTyped: "Typed PDF, read directly",
  readOcr: "Scanned, read with OCR",
  readDocx: "Word document, read directly",
  wOcr: "This was read with OCR, which can misread dates and digits. Check them against your original.",
  wNoText: "No text was found in this file. Enter the date yourself and describe what happened below, or try a clearer scan.",
  wTruncated: "The text was cut at the limit, so the end of the document was not read.",
  wMultiple: "Several dates were found. Choose the date of the offence.",
  wPages: "Some pages were skipped and not read.",
  wPassword: "This file is password-protected, so its text could not be read.",
  dateTitle: "Offence date",
  dateNone: "No date was found. Enter the date of the offence.",
  dateManualOption: "A different date",
  dateInputLabel: "Offence date",
  dateConfirm: "I have checked this date against my document. It is the date of the offence.",
  dateEditedNote: "You changed the date, so it will be recorded as entered by you.",
  descTitle: "Describe what happened",
  descHelp: "Write two or three sentences about what happened (who did what, and to whom). The date comes from the document.",
  descCount: (n, max) => `${n} of ${max} characters (at least 20)`,
  descShort: "Write at least 20 characters about what happened to continue.",
  textReadTitle: "Text read from the document",
  textReadNote: "Scanned text can contain mistakes. Use it to check the date, or copy a sentence into your description if you want.",
  needConfirm: "Confirm the date to continue.",
  dzTitle: "Drop a file here, or",
  dzChoose: "choose a file",
  dzTypes: "PDF, JPG, PNG or DOCX, up to 10 MB. English documents only.",
  dzBadType: "That file type isn't supported. Use a PDF, JPG, PNG or DOCX.",
  reading: "Reading the document…",
  dcLede: "Add a document and LawShift reads the date from it. You check the date and describe what happened before anything is used.",
  dcStoreNote:
    "The file and your description are stored in your account, visible only to you, until you delete them or delete your account. Documents can contain personal details: upload only what you are allowed to use.",
  dcUploadTitle: "Add a document",
  dcListTitle: "Your documents",
  colFile: "File",
  colSaved: "Saved",
  colRead: "How it was read",
  colDate: "Offence date",
  colSize: "Size",
  colActions: "Actions",
  useInWorkspace: "Use in Workspace",
  download: "Download",
  del: "Delete",
  delAll: "Delete all documents",
  delTitle: "Delete this document?",
  delBody: "The file and your description are deleted from your account. This can't be undone.",
  delConfirm: "Yes, delete it",
  delAllTitle: (n) => `Delete all ${n} documents?`,
  delAllBody: "Every file and every description are deleted from your account. This can't be undone.",
  delAllConfirm: "Yes, delete all",
  cancel: "Cancel",
  save: "Save document",
  saving: "Saving…",
  saved: "Saved to your account.",
  discard: "Discard",
  loading: "Loading your documents…",
  loadError: "Your documents could not be loaded.",
  retry: "Try again",
  emptyTitle: "No documents yet",
  emptyBody: "Documents you save appear here with how their text was read.",
  wsAttachTitle: "Attach a document",
  wsFrom: "From your documents",
  wsUpload: "Upload new",
  wsPick: "Choose a document",
  wsNone: "You have no saved documents yet. Use Upload new.",
  wsAttachOnly: "Attach for this chat only",
  wsSaveAttach: "Save and attach",
  wsAttachStored: "Attach to this chat",
  wsWorking: "Working…",
  wsChip: "Attached",
  wsThisChatOnly: "this chat only",
  wsSavedDoc: "saved in your account",
  wsChangeDate: "Change date",
  wsRemove: "Remove",
  wsAfter: "Attached. Ask a question about it, for example: Which section applies?",
  wsCancel: "Cancel",
  stFilesFailed:
    "Your saved documents could not be deleted, so your account was not deleted. You are still logged in. Try again.",
  err401: "Your session has ended. Log in again.",
  err413: "That file is too large. The limit is 10 MB.",
  err415: "That file type isn't supported. Use a PDF, JPG, PNG or DOCX.",
  err422: "That file could not be read. It may be empty, damaged or password-protected.",
  err429: "Too many documents have been read just now. Wait a while and try again.",
  err503: "The reading service is busy or not running. Try again in a moment.",
  errNetwork: "The server could not be reached. Check that it is running and try again.",
  errGeneric: "Something went wrong. Try again.",
  errSave: "The document could not be saved. Nothing was stored. Try again.",
  errDelete: "The document could not be deleted. Try again.",
  errDownload: "A download link could not be made. Try again.",
  errAttach: "The document could not be attached. Check the date and your description, then try again.",
  errDetach: "The document could not be removed from this chat. Try again.",
};

const hi: DocCopy = {
  // Agent drafts: need native review.
  rvTitle: "जो पढ़ा गया उसे जाँचें",
  rvFile: "फ़ाइल",
  rvHow: "कैसे पढ़ा गया",
  readTyped: "टाइप किया PDF, सीधे पढ़ा गया",
  readOcr: "स्कैन किया, OCR से पढ़ा गया",
  readDocx: "Word दस्तावेज़, सीधे पढ़ा गया",
  wOcr: "इसे OCR से पढ़ा गया है, जो तिथियाँ और अंक गलत पढ़ सकता है। अपने मूल दस्तावेज़ से इन्हें मिलाकर देखें।",
  wNoText: "इस फ़ाइल में कोई पाठ नहीं मिला। तिथि खुद दर्ज करें और नीचे बताएँ क्या हुआ, या साफ़ स्कैन आज़माएँ।",
  wTruncated: "पाठ सीमा पर काट दिया गया, इसलिए दस्तावेज़ का अंतिम भाग पढ़ा नहीं गया।",
  wMultiple: "कई तिथियाँ मिलीं। अपराध की तिथि चुनें।",
  wPages: "कुछ पन्ने छोड़ दिए गए और पढ़े नहीं गए।",
  wPassword: "यह फ़ाइल पासवर्ड से सुरक्षित है, इसलिए इसका पाठ पढ़ा नहीं जा सका।",
  dateTitle: "अपराध की तिथि",
  dateNone: "कोई तिथि नहीं मिली। अपराध की तिथि दर्ज करें।",
  dateManualOption: "कोई और तिथि",
  dateInputLabel: "अपराध की तिथि",
  dateConfirm: "मैंने इस तिथि को अपने दस्तावेज़ से मिला लिया है। यही अपराध की तिथि है।",
  dateEditedNote: "आपने तिथि बदली है, इसलिए इसे आपके द्वारा दर्ज की गई के रूप में दर्ज किया जाएगा।",
  descTitle: "बताएँ क्या हुआ",
  descHelp: "दो-तीन वाक्यों में लिखें कि क्या हुआ (किसने क्या किया, और किसके साथ)। तिथि दस्तावेज़ से ली जाती है।",
  descCount: (n, max) => `${max} में से ${n} अक्षर (कम से कम 20)`,
  descShort: "आगे बढ़ने के लिए क्या हुआ, इसके बारे में कम से कम 20 अक्षर लिखें।",
  textReadTitle: "दस्तावेज़ से पढ़ा गया पाठ",
  textReadNote: "स्कैन किए पाठ में गलतियाँ हो सकती हैं। इससे तिथि जाँचें, या चाहें तो एक वाक्य अपने विवरण में कॉपी करें।",
  needConfirm: "आगे बढ़ने के लिए तिथि की पुष्टि करें।",
  dzTitle: "फ़ाइल यहाँ छोड़ें, या",
  dzChoose: "फ़ाइल चुनें",
  dzTypes: "PDF, JPG, PNG या DOCX, 10 MB तक। केवल अंग्रेज़ी दस्तावेज़।",
  dzBadType: "यह फ़ाइल प्रकार समर्थित नहीं है। PDF, JPG, PNG या DOCX का उपयोग करें।",
  reading: "दस्तावेज़ पढ़ा जा रहा है…",
  dcLede: "दस्तावेज़ जोड़ें, LawShift उससे तिथि पढ़ लेगा। कुछ भी उपयोग होने से पहले आप तिथि जाँचते हैं और बताते हैं कि क्या हुआ।",
  dcStoreNote:
    "फ़ाइल और आपका विवरण आपके खाते में सहेजा जाता है, केवल आपको दिखता है, जब तक आप उन्हें या अपना खाता नहीं हटाते। दस्तावेज़ों में निजी जानकारी हो सकती है: केवल वही अपलोड करें जिसका उपयोग करने की आपको अनुमति है।",
  dcUploadTitle: "दस्तावेज़ जोड़ें",
  dcListTitle: "आपके दस्तावेज़",
  colFile: "फ़ाइल",
  colSaved: "सहेजा गया",
  colRead: "कैसे पढ़ा गया",
  colDate: "अपराध की तिथि",
  colSize: "आकार",
  colActions: "कार्रवाई",
  useInWorkspace: "वर्कस्पेस में उपयोग करें",
  download: "डाउनलोड",
  del: "हटाएँ",
  delAll: "सभी दस्तावेज़ हटाएँ",
  delTitle: "यह दस्तावेज़ हटाएँ?",
  delBody: "फ़ाइल और आपका विवरण आपके खाते से हट जाएगा। इसे वापस नहीं किया जा सकता।",
  delConfirm: "हाँ, हटाएँ",
  delAllTitle: (n) => `सभी ${n} दस्तावेज़ हटाएँ?`,
  delAllBody: "हर फ़ाइल और हर विवरण आपके खाते से हट जाएगा। इसे वापस नहीं किया जा सकता।",
  delAllConfirm: "हाँ, सब हटाएँ",
  cancel: "रद्द करें",
  save: "दस्तावेज़ सहेजें",
  saving: "सहेजा जा रहा है…",
  saved: "आपके खाते में सहेजा गया।",
  discard: "छोड़ दें",
  loading: "आपके दस्तावेज़ लोड हो रहे हैं…",
  loadError: "आपके दस्तावेज़ लोड नहीं हो सके।",
  retry: "दोबारा कोशिश करें",
  emptyTitle: "अभी कोई दस्तावेज़ नहीं",
  emptyBody: "आपके सहेजे दस्तावेज़ यहाँ दिखेंगे, साथ में कि उनका पाठ कैसे पढ़ा गया।",
  wsAttachTitle: "दस्तावेज़ जोड़ें",
  wsFrom: "आपके दस्तावेज़ों से",
  wsUpload: "नया अपलोड करें",
  wsPick: "दस्तावेज़ चुनें",
  wsNone: "आपके पास अभी कोई सहेजा दस्तावेज़ नहीं है। नया अपलोड करें चुनें।",
  wsAttachOnly: "केवल इस चैट के लिए जोड़ें",
  wsSaveAttach: "सहेजें और जोड़ें",
  wsAttachStored: "इस चैट में जोड़ें",
  wsWorking: "काम हो रहा है…",
  wsChip: "जोड़ा गया",
  wsThisChatOnly: "केवल इस चैट के लिए",
  wsSavedDoc: "आपके खाते में सहेजा",
  wsChangeDate: "तिथि बदलें",
  wsRemove: "हटाएँ",
  wsAfter: "जोड़ दिया गया। इसके बारे में प्रश्न पूछें, जैसे: कौन सी धारा लागू होती है?",
  wsCancel: "रद्द करें",
  stFilesFailed:
    "आपके सहेजे दस्तावेज़ हटाए नहीं जा सके, इसलिए आपका खाता नहीं हटाया गया। आप अब भी लॉग इन हैं। दोबारा कोशिश करें।",
  err401: "आपका सत्र समाप्त हो गया है। फिर से लॉग इन करें।",
  err413: "यह फ़ाइल बहुत बड़ी है। सीमा 10 MB है।",
  err415: "यह फ़ाइल प्रकार समर्थित नहीं है। PDF, JPG, PNG या DOCX का उपयोग करें।",
  err422: "यह फ़ाइल पढ़ी नहीं जा सकी। यह खाली, क्षतिग्रस्त या पासवर्ड से सुरक्षित हो सकती है।",
  err429: "अभी बहुत सारे दस्तावेज़ पढ़े जा चुके हैं। थोड़ी देर रुककर दोबारा कोशिश करें।",
  err503: "पढ़ने वाली सेवा व्यस्त है या चल नहीं रही। थोड़ी देर में दोबारा कोशिश करें।",
  errNetwork: "सर्वर से संपर्क नहीं हो सका। जाँचें कि वह चल रहा है और दोबारा कोशिश करें।",
  errGeneric: "कुछ गड़बड़ हो गई। दोबारा कोशिश करें।",
  errSave: "दस्तावेज़ सहेजा नहीं जा सका। कुछ भी संग्रहीत नहीं हुआ। दोबारा कोशिश करें।",
  errDelete: "दस्तावेज़ हटाया नहीं जा सका। दोबारा कोशिश करें।",
  errDownload: "डाउनलोड लिंक नहीं बन सका। दोबारा कोशिश करें।",
  errAttach: "दस्तावेज़ जोड़ा नहीं जा सका। तिथि और अपना विवरण जाँचें, फिर दोबारा कोशिश करें।",
  errDetach: "दस्तावेज़ इस चैट से हटाया नहीं जा सका। दोबारा कोशिश करें।",
};

const mr: DocCopy = {
  // Agent drafts: need native review.
  rvTitle: "काय वाचले गेले ते तपासा",
  rvFile: "फाइल",
  rvHow: "कसे वाचले गेले",
  readTyped: "टाइप केलेला PDF, थेट वाचला",
  readOcr: "स्कॅन केलेला, OCR ने वाचला",
  readDocx: "Word दस्तऐवज, थेट वाचला",
  wOcr: "हे OCR ने वाचले आहे, जे तारखा आणि अंक चुकीचे वाचू शकते. तुमच्या मूळ दस्तऐवजाशी ते पडताळून पहा.",
  wNoText: "या फाइलमध्ये मजकूर आढळला नाही. तारीख स्वतः भरा आणि खाली काय घडले ते सांगा, किंवा अधिक स्पष्ट स्कॅन वापरून पहा.",
  wTruncated: "मजकूर मर्यादेवर कापला गेला, त्यामुळे दस्तऐवजाचा शेवटचा भाग वाचला गेला नाही.",
  wMultiple: "अनेक तारखा आढळल्या. गुन्ह्याची तारीख निवडा.",
  wPages: "काही पाने वगळली गेली आणि वाचली गेली नाहीत.",
  wPassword: "ही फाइल पासवर्डने सुरक्षित आहे, त्यामुळे तिचा मजकूर वाचता आला नाही.",
  dateTitle: "गुन्ह्याची तारीख",
  dateNone: "कोणतीही तारीख आढळली नाही. गुन्ह्याची तारीख भरा.",
  dateManualOption: "दुसरी तारीख",
  dateInputLabel: "गुन्ह्याची तारीख",
  dateConfirm: "मी ही तारीख माझ्या दस्तऐवजाशी पडताळली आहे. हीच गुन्ह्याची तारीख आहे.",
  dateEditedNote: "तुम्ही तारीख बदलली आहे, म्हणून ती तुम्ही भरलेली म्हणून नोंदवली जाईल.",
  descTitle: "काय घडले ते सांगा",
  descHelp: "दोन-तीन वाक्यांत लिहा काय घडले (कोणी काय केले, आणि कोणाशी). तारीख दस्तऐवजातून घेतली जाते.",
  descCount: (n, max) => `${max} पैकी ${n} अक्षरे (किमान 20)`,
  descShort: "पुढे जाण्यासाठी काय घडले याबद्दल किमान 20 अक्षरे लिहा.",
  textReadTitle: "दस्तऐवजातून वाचलेला मजकूर",
  textReadNote: "स्कॅन केलेल्या मजकुरात चुका असू शकतात. त्यावरून तारीख तपासा, किंवा हवे असल्यास एक वाक्य तुमच्या वर्णनात कॉपी करा.",
  needConfirm: "पुढे जाण्यासाठी तारखेची पुष्टी करा.",
  dzTitle: "फाइल येथे टाका, किंवा",
  dzChoose: "फाइल निवडा",
  dzTypes: "PDF, JPG, PNG किंवा DOCX, 10 MB पर्यंत. फक्त इंग्रजी दस्तऐवज.",
  dzBadType: "हा फाइल प्रकार समर्थित नाही. PDF, JPG, PNG किंवा DOCX वापरा.",
  reading: "दस्तऐवज वाचला जात आहे…",
  dcLede: "दस्तऐवज जोडा, LawShift त्यातून तारीख वाचेल. काहीही वापरले जाण्यापूर्वी तुम्ही तारीख तपासता आणि काय घडले ते सांगता.",
  dcStoreNote:
    "फाइल आणि तुमचे वर्णन तुमच्या खात्यात जतन केले जाते, फक्त तुम्हाला दिसते, जोपर्यंत तुम्ही तो किंवा तुमचे खाते हटवत नाही. दस्तऐवजांमध्ये वैयक्तिक माहिती असू शकते: फक्त तेच अपलोड करा जे वापरण्याची तुम्हाला परवानगी आहे.",
  dcUploadTitle: "दस्तऐवज जोडा",
  dcListTitle: "तुमचे दस्तऐवज",
  colFile: "फाइल",
  colSaved: "जतन केले",
  colRead: "कसे वाचले गेले",
  colDate: "गुन्ह्याची तारीख",
  colSize: "आकार",
  colActions: "कृती",
  useInWorkspace: "वर्कस्पेसमध्ये वापरा",
  download: "डाउनलोड",
  del: "हटवा",
  delAll: "सर्व दस्तऐवज हटवा",
  delTitle: "हा दस्तऐवज हटवायचा?",
  delBody: "फाइल आणि तुमचे वर्णन तुमच्या खात्यातून हटवले जाईल. हे परत करता येणार नाही.",
  delConfirm: "होय, हटवा",
  delAllTitle: (n) => `सर्व ${n} दस्तऐवज हटवायचे?`,
  delAllBody: "प्रत्येक फाइल आणि प्रत्येक वर्णन तुमच्या खात्यातून हटवले जाईल. हे परत करता येणार नाही.",
  delAllConfirm: "होय, सर्व हटवा",
  cancel: "रद्द करा",
  save: "दस्तऐवज जतन करा",
  saving: "जतन होत आहे…",
  saved: "तुमच्या खात्यात जतन केले.",
  discard: "सोडून द्या",
  loading: "तुमचे दस्तऐवज लोड होत आहेत…",
  loadError: "तुमचे दस्तऐवज लोड करता आले नाहीत.",
  retry: "पुन्हा प्रयत्न करा",
  emptyTitle: "अजून दस्तऐवज नाहीत",
  emptyBody: "तुम्ही जतन केलेले दस्तऐवज येथे दिसतील, त्यांचा मजकूर कसा वाचला गेला यासह.",
  wsAttachTitle: "दस्तऐवज जोडा",
  wsFrom: "तुमच्या दस्तऐवजांतून",
  wsUpload: "नवीन अपलोड करा",
  wsPick: "दस्तऐवज निवडा",
  wsNone: "तुमच्याकडे अजून जतन केलेले दस्तऐवज नाहीत. नवीन अपलोड करा वापरा.",
  wsAttachOnly: "फक्त या चॅटसाठी जोडा",
  wsSaveAttach: "जतन करा आणि जोडा",
  wsAttachStored: "या चॅटमध्ये जोडा",
  wsWorking: "काम सुरू आहे…",
  wsChip: "जोडले",
  wsThisChatOnly: "फक्त या चॅटसाठी",
  wsSavedDoc: "तुमच्या खात्यात जतन केले",
  wsChangeDate: "तारीख बदला",
  wsRemove: "काढा",
  wsAfter: "जोडले. त्याबद्दल प्रश्न विचारा, उदाहरणार्थ: कोणते कलम लागू होते?",
  wsCancel: "रद्द करा",
  stFilesFailed:
    "तुमचे जतन केलेले दस्तऐवज हटवता आले नाहीत, म्हणून तुमचे खाते हटवले गेले नाही. तुम्ही अजूनही लॉग इन आहात. पुन्हा प्रयत्न करा.",
  err401: "तुमचे सत्र संपले आहे. पुन्हा लॉग इन करा.",
  err413: "ही फाइल खूप मोठी आहे. मर्यादा 10 MB आहे.",
  err415: "हा फाइल प्रकार समर्थित नाही. PDF, JPG, PNG किंवा DOCX वापरा.",
  err422: "ही फाइल वाचता आली नाही. ती रिकामी, खराब किंवा पासवर्डने सुरक्षित असू शकते.",
  err429: "आत्ता खूप दस्तऐवज वाचले गेले आहेत. थोडा वेळ थांबून पुन्हा प्रयत्न करा.",
  err503: "वाचन सेवा व्यस्त आहे किंवा चालू नाही. थोड्या वेळाने पुन्हा प्रयत्न करा.",
  errNetwork: "सर्व्हरशी संपर्क होऊ शकला नाही. तो चालू आहे का ते तपासा आणि पुन्हा प्रयत्न करा.",
  errGeneric: "काहीतरी चुकले. पुन्हा प्रयत्न करा.",
  errSave: "दस्तऐवज जतन करता आला नाही. काहीही साठवले गेले नाही. पुन्हा प्रयत्न करा.",
  errDelete: "दस्तऐवज हटवता आला नाही. पुन्हा प्रयत्न करा.",
  errDownload: "डाउनलोड लिंक तयार करता आली नाही. पुन्हा प्रयत्न करा.",
  errAttach: "दस्तऐवज जोडता आला नाही. तारीख आणि तुमचे वर्णन तपासा, मग पुन्हा प्रयत्न करा.",
  errDetach: "दस्तऐवज या चॅटमधून काढता आला नाही. पुन्हा प्रयत्न करा.",
};

const DICTS: Record<Lang, DocCopy> = { en, hi, mr };

export function getDocCopy(lang: Lang): DocCopy {
  return DICTS[lang] ?? en;
}
