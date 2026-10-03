import type { Lang } from "./prefs";

/** Copy for the sign-in screens (EN / HI / MR). */
export type AuthCopy = {
  previewNote: string;
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
  registerSuccessTitle: string;
  haveAccount: string;
  loginLink: string;

  loginTitle: string;
  loginLede: string;
  forgot: string;
  logIn: string;
  loggingIn: string;
  loginSuccessTitle: string;
  newHere: string;
  registerLink: string;

  forgotTitle: string;
  forgotLede: string;
  sendLink: string;
  sending: string;
  forgotSuccessTitle: string;
  forgotSuccessBody: string;
  backToLogin: string;

  successBody: string;
  continueTo: string;
};

const en: AuthCopy = {
  backHome: "Back to home",
  previewNote:
    "Preview: sign-in isn't connected yet. This screen shows how it will work. Nothing you type is sent or saved.",
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
  registerSuccessTitle: "Account created",
  haveAccount: "Already have an account?",
  loginLink: "Log in",

  loginTitle: "Log in",
  loginLede: "Use the email and password for your account.",
  forgot: "Forgot password?",
  logIn: "Log in",
  loggingIn: "Logging in…",
  loginSuccessTitle: "Logged in",
  newHere: "New here?",
  registerLink: "Register",

  forgotTitle: "Reset your password",
  forgotLede: "Enter your email address and we'll send a reset link.",
  sendLink: "Send reset link",
  sending: "Sending…",
  forgotSuccessTitle: "Check your email",
  forgotSuccessBody: "Placeholder: no email has been sent.",
  backToLogin: "Back to log in",

  successBody: "Placeholder sign-in complete. Taking you to your dashboard…",
  continueTo: "Go to dashboard",
};

const hi: AuthCopy = {
  backHome: "होम पर वापस जाएँ",
  previewNote:
    "पूर्वावलोकन: साइन-इन अभी जुड़ा नहीं है। यह स्क्रीन दिखाती है कि यह कैसे काम करेगा। आप जो टाइप करते हैं वह भेजा या सहेजा नहीं जाता।",
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
  registerSuccessTitle: "खाता बन गया",
  haveAccount: "पहले से खाता है?",
  loginLink: "लॉग इन करें",

  loginTitle: "लॉग इन करें",
  loginLede: "अपने खाते का ईमेल और पासवर्ड इस्तेमाल करें।",
  forgot: "पासवर्ड भूल गए?",
  logIn: "लॉग इन करें",
  loggingIn: "लॉग इन हो रहा है…",
  loginSuccessTitle: "लॉग इन हो गया",
  newHere: "नए हैं?",
  registerLink: "पंजीकरण करें",

  forgotTitle: "पासवर्ड रीसेट करें",
  forgotLede: "अपना ईमेल पता लिखें, हम रीसेट लिंक भेजेंगे।",
  sendLink: "रीसेट लिंक भेजें",
  sending: "भेजा जा रहा है…",
  forgotSuccessTitle: "अपना ईमेल देखें",
  forgotSuccessBody: "प्लेसहोल्डर: कोई ईमेल नहीं भेजा गया है।",
  backToLogin: "लॉग इन पर वापस जाएँ",

  successBody: "प्लेसहोल्डर साइन-इन पूरा हुआ। आपको आपके डैशबोर्ड पर ले जाया जा रहा है…",
  continueTo: "डैशबोर्ड पर जाएँ",
};

const mr: AuthCopy = {
  backHome: "मुख्यपृष्ठावर परत जा",
  previewNote:
    "पूर्वावलोकन: साइन-इन अजून जोडलेले नाही. हा स्क्रीन ते कसे चालेल ते दाखवतो. तुम्ही टाइप केलेले काहीही पाठवले किंवा जतन केले जात नाही.",
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
  registerSuccessTitle: "खाते तयार झाले",
  haveAccount: "आधीच खाते आहे?",
  loginLink: "लॉग इन करा",

  loginTitle: "लॉग इन करा",
  loginLede: "तुमच्या खात्याचा ईमेल आणि पासवर्ड वापरा.",
  forgot: "पासवर्ड विसरलात?",
  logIn: "लॉग इन करा",
  loggingIn: "लॉग इन होत आहे…",
  loginSuccessTitle: "लॉग इन झाले",
  newHere: "नवीन आहात?",
  registerLink: "नोंदणी करा",

  forgotTitle: "पासवर्ड रीसेट करा",
  forgotLede: "तुमचा ईमेल पत्ता लिहा, आम्ही रीसेट लिंक पाठवू.",
  sendLink: "रीसेट लिंक पाठवा",
  sending: "पाठवत आहे…",
  forgotSuccessTitle: "तुमचा ईमेल तपासा",
  forgotSuccessBody: "प्लेसहोल्डर: कोणताही ईमेल पाठवलेला नाही.",
  backToLogin: "लॉग इनकडे परत जा",

  successBody: "प्लेसहोल्डर साइन-इन पूर्ण झाले. तुम्हाला तुमच्या डॅशबोर्डवर नेले जात आहे…",
  continueTo: "डॅशबोर्डवर जा",
};

const DICTS: Record<Lang, AuthCopy> = { en, hi, mr };

export function getAuthCopy(lang: Lang): AuthCopy {
  return DICTS[lang] ?? en;
}
