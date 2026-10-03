"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { getDictionary, type Dictionary } from "./i18n";

export type Lang = "en" | "hi" | "mr";

type AppPrefs = {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: Dictionary;
};

const PrefsContext = createContext<AppPrefs | null>(null);

export function PrefsProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>("en");

  useEffect(() => {
    const storedLang = window.localStorage.getItem("lawshift-lang") as Lang | null;
    if (storedLang === "en" || storedLang === "hi" || storedLang === "mr") {
      setLang(storedLang);
      document.documentElement.lang = storedLang === "en" ? "en" : storedLang;
    }
    // Drop any legacy theme preference — site is dark-only.
    window.localStorage.removeItem("lawshift-theme");
    document.documentElement.removeAttribute("data-theme");
  }, []);

  const setLangPersist = useCallback((l: Lang) => {
    setLang(l);
    window.localStorage.setItem("lawshift-lang", l);
    document.documentElement.lang = l === "en" ? "en" : l;
  }, []);

  const t = useMemo(() => getDictionary(lang), [lang]);

  const value = useMemo(
    () => ({
      lang,
      setLang: setLangPersist,
      t,
    }),
    [lang, setLangPersist, t],
  );

  return (
    <PrefsContext.Provider value={value}>
      {children}
    </PrefsContext.Provider>
  );
}

export function usePrefs() {
  const ctx = useContext(PrefsContext);
  if (!ctx) throw new Error("usePrefs must be used within PrefsProvider");
  return ctx;
}

export function useT() {
  return usePrefs().t;
}
