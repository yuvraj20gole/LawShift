import type { Metadata } from "next";
import {
  Literata,
  Noto_Sans_Devanagari,
  Noto_Serif_Devanagari,
  Public_Sans,
} from "next/font/google";
import { PrefsProvider } from "@/lib/prefs";
import { SmoothScroll } from "@/components/SmoothScroll";
import "lenis/dist/lenis.css";
import "./globals.css";

const literata = Literata({
  subsets: ["latin"],
  style: ["normal", "italic"],
  axes: ["opsz"],
  variable: "--font-literata",
  display: "swap",
});

const publicSans = Public_Sans({
  subsets: ["latin"],
  variable: "--font-public-sans",
  display: "swap",
});

/* Hindi and Marathi answers render in these instead of a browser fallback. */
const notoSerifDevanagari = Noto_Serif_Devanagari({
  subsets: ["devanagari"],
  weight: ["400", "600"],
  variable: "--font-noto-serif-deva",
  display: "swap",
  preload: false,
});

const notoSansDevanagari = Noto_Sans_Devanagari({
  subsets: ["devanagari"],
  weight: ["400", "600"],
  variable: "--font-noto-sans-deva",
  display: "swap",
  preload: false,
});

export const metadata: Metadata = {
  title: "LawShift — which law applies, IPC or BNS",
  description:
    "Describe a case and LawShift works out whether the Indian Penal Code or the Bharatiya Nyaya Sanhita applies, then shows the section as written. An informational research tool, not legal advice.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${literata.variable} ${publicSans.variable} ${notoSerifDevanagari.variable} ${notoSansDevanagari.variable}`}
      >
        <PrefsProvider>
          <SmoothScroll />
          {children}
        </PrefsProvider>
      </body>
    </html>
  );
}
