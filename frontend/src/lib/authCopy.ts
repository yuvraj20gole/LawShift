import type { Lang } from "./prefs";

/** Copy for the sign-in screens (EN / HI / MR). */
export type AuthCopy = {
  backHome: string;
  emailLabel: string;
  passwordLabel: string;
  confirmLabel: string;
  show: string;
  hide: string;
  emailRequired: string;
  emailInvalid: string;
  passwordRequired: string;
  confirmRequired: string;
  mismatch: string;
  matchOk: string;

  registerTitle: string;
  registerLede: string;
  rulesTitle: string;
  rule1: string;
  rule2: string;
  rule3: string;
  rule4: string;
  rule5: string;
  rulesMet: (n: number) => string;
  met: string;
  notMet: string;
  createAccount: string;
  creating: string;
  disabledHint: string;
  haveAccount: string;
  loginLink: string;

  loginTitle: string;
  loginLede: string;
  forgot: string;
  logIn: string;
  loggingIn: string;
  newHere: string;
  registerLink: string;

  forgotTitle: string;
  forgotLede: string;
  backToLogin: string;
  errInvalid: string;
  errUnconfirmed: string;
  errRate: string;
  errExists: string;
  errWeak: string;
  errSignupOff: string;
  errGeneric: string;
  errSamePassword: string;
  errReauth: string;
  registerSavedNote: string;
  accountDeleted: string;
  confirmTitle: string;
  confirmBody: string;

  forgotSend: string;
  forgotSending: string;
  forgotSentTitle: string;
  forgotSentBody: string;
  resetTitle: string;
  resetLede: string;
  resetChecking: string;
  newPasswordLabel: string;
  resetSubmit: string;
  resetSaving: string;
  resetLinkBadTitle: string;
  resetLinkBadBody: string;
  requestNewLink: string;
  resetDone: string;
};

const en: AuthCopy = {
  backHome: "Back to home",
  emailLabel: "Email",
  passwordLabel: "Password",
  confirmLabel: "Confirm password",
  show: "Show",
  hide: "Hide",
  emailRequired: "Enter your email address.",
  emailInvalid:
    "That doesn't look like an email address. Check for a missing @ or domain, such as name@example.com.",
  passwordRequired: "Enter your password.",
  confirmRequired: "Re-enter your password to confirm it.",
  mismatch: "The two passwords don't match yet.",
  matchOk: "Passwords match",

  registerTitle: "Create an account",
  registerLede: "Register with an email address and a password.",
  rulesTitle: "Your password needs",
  rule1: "At least 8 characters",
  rule2: "One uppercase letter",
  rule3: "One lowercase letter",
  rule4: "One number",
  rule5: "One special character, for example ! @ # $ % ^ & *",
  rulesMet: (n) => `${n} of 5 requirements met`,
  met: "met",
  notMet: "not met yet",
  createAccount: "Create account",
  creating: "Creating account…",
  disabledHint:
    "Meet every password requirement and match both passwords to continue.",
  haveAccount: "Already have an account?",
  loginLink: "Log in",

  loginTitle: "Log in",
  loginLede: "Use the email and password for your account.",
  forgot: "Forgot password?",
  logIn: "Log in",
  loggingIn: "Logging in…",
  newHere: "New here?",
  registerLink: "Register",

  forgotTitle: "Reset your password",
  forgotLede: "Enter your email address and we will send you a link to set a new password.",
  backToLogin: "Back to log in",
  errInvalid:
    "The email or password is wrong. Check both and try again.",
  errUnconfirmed:
    "This email address has not been confirmed yet. Open the confirmation link we sent you, then log in.",
  errRate:
    "Too many attempts. Wait a few minutes and try again.",
  errExists:
    "An account with this email already exists. Log in instead.",
  errWeak:
    "The server rejected this password. Choose a longer or less common one.",
  errSignupOff:
    "New registrations are closed right now.",
  errGeneric:
    "Something went wrong on our side. Try again in a moment.",
  errSamePassword:
    "The new password is the same as your current one. Choose a different password.",
  errReauth:
    "For security, log in again, then change your password.",
  registerSavedNote:
    "When you are logged in, your questions are saved in your account history, and documents you choose to save, with your description, are stored in your account. You can delete them, or your account, at any time.",
  accountDeleted:
    "Your account was deleted.",
  confirmTitle:
    "Check your email",
  confirmBody:
    "We sent a confirmation link to your address. Open it to finish creating your account, then log in.",

  forgotSend: "Send reset link",
  forgotSending: "Sending…",
  forgotSentTitle: "Check your email",
  forgotSentBody:
    "If an account exists for that address, we have sent a link to reset the password. The link works once and expires after a while. If nothing arrives, check your spam folder.",
  resetTitle: "Set a new password",
  resetLede: "Choose a new password for your account.",
  resetChecking: "Checking your reset link…",
  newPasswordLabel: "New password",
  resetSubmit: "Save new password",
  resetSaving: "Saving…",
  resetLinkBadTitle: "This reset link cannot be used",
  resetLinkBadBody:
    "The link may have expired, been used already, or been opened in a different browser from the one where you asked for it. Request a new link and open it in the same browser.",
  requestNewLink: "Request a new link",
  resetDone: "Your password was changed. Log in with the new password.",
};

const hi: AuthCopy = {
  backHome: "होम पर वापस जाएँ",
  emailLabel: "ईमेल",
  passwordLabel: "पासवर्ड",
  confirmLabel: "पासवर्ड की पुष्टि करें",
  show: "दिखाएँ",
  hide: "छिपाएँ",
  emailRequired: "अपना ईमेल पता लिखें।",
  emailInvalid:
    "यह ईमेल पते जैसा नहीं दिखता। @ या डोमेन छूटा तो नहीं, जैसे name@example.com।",
  passwordRequired: "अपना पासवर्ड लिखें।",
  confirmRequired: "पुष्टि के लिए पासवर्ड फिर से लिखें।",
  mismatch: "दोनों पासवर्ड अभी मेल नहीं खाते।",
  matchOk: "पासवर्ड मेल खाते हैं",

  registerTitle: "खाता बनाएँ",
  registerLede: "ईमेल पते और पासवर्ड से पंजीकरण करें।",
  rulesTitle: "आपके पासवर्ड में होना चाहिए",
  rule1: "कम से कम 8 अक्षर",
  rule2: "एक बड़ा (अपरकेस) अक्षर",
  rule3: "एक छोटा (लोअरकेस) अक्षर",
  rule4: "एक अंक",
  rule5: "एक विशेष चिह्न, जैसे ! @ # $ % ^ & *",
  rulesMet: (n) => `5 में से ${n} शर्तें पूरी`,
  met: "पूरी",
  notMet: "अभी पूरी नहीं",
  createAccount: "खाता बनाएँ",
  creating: "खाता बनाया जा रहा है…",
  disabledHint:
    "आगे बढ़ने के लिए पासवर्ड की हर शर्त पूरी करें और दोनों पासवर्ड मिलाएँ।",
  haveAccount: "पहले से खाता है?",
  loginLink: "लॉग इन करें",

  loginTitle: "लॉग इन करें",
  loginLede: "अपने खाते का ईमेल और पासवर्ड इस्तेमाल करें।",
  forgot: "पासवर्ड भूल गए?",
  logIn: "लॉग इन करें",
  loggingIn: "लॉग इन हो रहा है…",
  newHere: "नए हैं?",
  registerLink: "पंजीकरण करें",

  forgotTitle: "पासवर्ड रीसेट करें",
  forgotLede: "अपना ईमेल पता लिखें, हम नया पासवर्ड सेट करने का लिंक भेजेंगे।",
  backToLogin: "लॉग इन पर वापस जाएँ",
  errInvalid:
    "ईमेल या पासवर्ड गलत है। दोनों जाँचकर फिर कोशिश करें।",
  errUnconfirmed:
    "इस ईमेल पते की पुष्टि अभी नहीं हुई है। हमारे भेजे पुष्टि लिंक को खोलें, फिर लॉग इन करें।",
  errRate:
    "बहुत ज़्यादा प्रयास हो गए। कुछ मिनट रुककर फिर कोशिश करें।",
  errExists:
    "इस ईमेल से खाता पहले से मौजूद है। इसके बजाय लॉग इन करें।",
  errWeak:
    "सर्वर ने यह पासवर्ड स्वीकार नहीं किया। कोई लंबा या कम आम पासवर्ड चुनें।",
  errSignupOff:
    "अभी नए पंजीकरण बंद हैं।",
  errGeneric:
    "हमारी ओर से कुछ गड़बड़ हो गई। थोड़ी देर में फिर कोशिश करें।",
  errSamePassword:
    "नया पासवर्ड आपके मौजूदा पासवर्ड जैसा ही है। कोई अलग पासवर्ड चुनें।",
  errReauth:
    "सुरक्षा के लिए फिर से लॉग इन करें, फिर पासवर्ड बदलें।",
  registerSavedNote:
    "लॉग इन रहने पर आपके प्रश्न आपके खाते के इतिहास में सहेजे जाते हैं, और जो दस्तावेज़ आप सहेजना चुनते हैं, आपके विवरण के साथ, आपके खाते में रखे जाते हैं। आप उन्हें, या अपना खाता, कभी भी हटा सकते हैं।",
  accountDeleted:
    "आपका खाता हटा दिया गया।",
  confirmTitle:
    "अपना ईमेल देखें",
  confirmBody:
    "हमने आपके पते पर पुष्टि लिंक भेजा है। खाता पूरा करने के लिए उसे खोलें, फिर लॉग इन करें।",

  forgotSend: "रीसेट लिंक भेजें",
  forgotSending: "भेजा जा रहा है…",
  forgotSentTitle: "अपना ईमेल देखें",
  forgotSentBody:
    "अगर इस पते से कोई खाता है, तो हमने पासवर्ड रीसेट करने का लिंक भेजा है। लिंक एक ही बार काम करता है और कुछ समय बाद समाप्त हो जाता है। कुछ न आए तो स्पैम फ़ोल्डर देखें।",
  resetTitle: "नया पासवर्ड सेट करें",
  resetLede: "अपने खाते के लिए नया पासवर्ड चुनें।",
  resetChecking: "आपका रीसेट लिंक जाँचा जा रहा है…",
  newPasswordLabel: "नया पासवर्ड",
  resetSubmit: "नया पासवर्ड सहेजें",
  resetSaving: "सहेजा जा रहा है…",
  resetLinkBadTitle: "यह रीसेट लिंक इस्तेमाल नहीं हो सकता",
  resetLinkBadBody:
    "हो सकता है लिंक की अवधि समाप्त हो गई हो, वह पहले इस्तेमाल हो चुका हो, या उसे उस ब्राउज़र से अलग ब्राउज़र में खोला गया हो जिसमें आपने अनुरोध किया था। नया लिंक माँगें और उसे उसी ब्राउज़र में खोलें।",
  requestNewLink: "नया लिंक माँगें",
  resetDone: "आपका पासवर्ड बदल दिया गया। नए पासवर्ड से लॉग इन करें।",
};

const mr: AuthCopy = {
  backHome: "मुख्यपृष्ठावर परत जा",
  emailLabel: "ईमेल",
  passwordLabel: "पासवर्ड",
  confirmLabel: "पासवर्डची पुष्टी करा",
  show: "दाखवा",
  hide: "लपवा",
  emailRequired: "तुमचा ईमेल पत्ता लिहा.",
  emailInvalid:
    "हे ईमेल पत्त्यासारखे दिसत नाही. @ किंवा डोमेन राहिले नाही ना, उदा. name@example.com.",
  passwordRequired: "तुमचा पासवर्ड लिहा.",
  confirmRequired: "पुष्टीसाठी पासवर्ड पुन्हा लिहा.",
  mismatch: "दोन्ही पासवर्ड अजून जुळत नाहीत.",
  matchOk: "पासवर्ड जुळतात",

  registerTitle: "खाते तयार करा",
  registerLede: "ईमेल पत्ता आणि पासवर्डने नोंदणी करा.",
  rulesTitle: "तुमच्या पासवर्डमध्ये हवे",
  rule1: "किमान 8 अक्षरे",
  rule2: "एक मोठे (अपरकेस) अक्षर",
  rule3: "एक लहान (लोअरकेस) अक्षर",
  rule4: "एक अंक",
  rule5: "एक विशेष चिन्ह, उदा. ! @ # $ % ^ & *",
  rulesMet: (n) => `5 पैकी ${n} अटी पूर्ण`,
  met: "पूर्ण",
  notMet: "अजून पूर्ण नाही",
  createAccount: "खाते तयार करा",
  creating: "खाते तयार होत आहे…",
  disabledHint:
    "पुढे जाण्यासाठी पासवर्डची प्रत्येक अट पूर्ण करा आणि दोन्ही पासवर्ड जुळवा.",
  haveAccount: "आधीच खाते आहे?",
  loginLink: "लॉग इन करा",

  loginTitle: "लॉग इन करा",
  loginLede: "तुमच्या खात्याचा ईमेल आणि पासवर्ड वापरा.",
  forgot: "पासवर्ड विसरलात?",
  logIn: "लॉग इन करा",
  loggingIn: "लॉग इन होत आहे…",
  newHere: "नवीन आहात?",
  registerLink: "नोंदणी करा",

  forgotTitle: "पासवर्ड रीसेट करा",
  forgotLede: "तुमचा ईमेल पत्ता लिहा, आम्ही नवीन पासवर्ड सेट करण्यासाठी लिंक पाठवू.",
  backToLogin: "लॉग इनकडे परत जा",
  errInvalid:
    "ईमेल किंवा पासवर्ड चुकीचा आहे. दोन्ही तपासून पुन्हा प्रयत्न करा.",
  errUnconfirmed:
    "या ईमेल पत्त्याची अजून पुष्टी झालेली नाही. आम्ही पाठवलेली पुष्टी लिंक उघडा, मग लॉग इन करा.",
  errRate:
    "खूप जास्त प्रयत्न झाले. काही मिनिटे थांबून पुन्हा प्रयत्न करा.",
  errExists:
    "या ईमेलने खाते आधीच अस्तित्वात आहे. त्याऐवजी लॉग इन करा.",
  errWeak:
    "सर्व्हरने हा पासवर्ड स्वीकारला नाही. जास्त लांब किंवा कमी सामान्य पासवर्ड निवडा.",
  errSignupOff:
    "सध्या नवीन नोंदणी बंद आहे.",
  errGeneric:
    "आमच्या बाजूने काहीतरी बिघडले. थोड्या वेळाने पुन्हा प्रयत्न करा.",
  errSamePassword:
    "नवीन पासवर्ड तुमच्या सध्याच्या पासवर्डसारखाच आहे. वेगळा पासवर्ड निवडा.",
  errReauth:
    "सुरक्षिततेसाठी पुन्हा लॉग इन करा, मग पासवर्ड बदला.",
  registerSavedNote:
    "लॉग इन असताना तुमचे प्रश्न तुमच्या खात्याच्या इतिहासात जतन केले जातात, आणि तुम्ही जतन करण्यासाठी निवडलेले दस्तऐवज, तुमच्या वर्णनासह, तुमच्या खात्यात साठवले जातात. तुम्ही ते, किंवा तुमचे खाते, केव्हाही हटवू शकता.",
  accountDeleted:
    "तुमचे खाते हटवले गेले.",
  confirmTitle:
    "तुमचा ईमेल तपासा",
  confirmBody:
    "आम्ही तुमच्या पत्त्यावर पुष्टी लिंक पाठवली आहे. खाते पूर्ण करण्यासाठी ती उघडा, मग लॉग इन करा.",

  forgotSend: "रीसेट लिंक पाठवा",
  forgotSending: "पाठवत आहे…",
  forgotSentTitle: "तुमचा ईमेल तपासा",
  forgotSentBody:
    "या पत्त्यावर खाते असल्यास, आम्ही पासवर्ड रीसेट करण्यासाठी लिंक पाठवली आहे. ही लिंक एकदाच चालते आणि काही वेळाने कालबाह्य होते. काही आले नाही तर स्पॅम फोल्डर तपासा.",
  resetTitle: "नवीन पासवर्ड सेट करा",
  resetLede: "तुमच्या खात्यासाठी नवीन पासवर्ड निवडा.",
  resetChecking: "तुमची रीसेट लिंक तपासली जात आहे…",
  newPasswordLabel: "नवीन पासवर्ड",
  resetSubmit: "नवीन पासवर्ड जतन करा",
  resetSaving: "जतन होत आहे…",
  resetLinkBadTitle: "ही रीसेट लिंक वापरता येत नाही",
  resetLinkBadBody:
    "लिंक कालबाह्य झाली असेल, आधीच वापरली गेली असेल, किंवा तुम्ही विनंती केलेल्या ब्राउझरपेक्षा वेगळ्या ब्राउझरमध्ये उघडली असेल. नवीन लिंक मागवा आणि ती त्याच ब्राउझरमध्ये उघडा.",
  requestNewLink: "नवीन लिंक मागवा",
  resetDone: "तुमचा पासवर्ड बदलला गेला. नवीन पासवर्डने लॉग इन करा.",
};

const DICTS: Record<Lang, AuthCopy> = { en, hi, mr };

export function getAuthCopy(lang: Lang): AuthCopy {
  return DICTS[lang] ?? en;
}
