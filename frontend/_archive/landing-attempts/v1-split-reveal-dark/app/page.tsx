import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { TrustStrip } from "@/components/TrustStrip";
import { ComparisonTable } from "@/components/ComparisonTable";
import { HowItWorks } from "@/components/HowItWorks";
import { ChatEntry } from "@/components/ChatEntry";
import { FAQ } from "@/components/FAQ";
import { Footer } from "@/components/Footer";

export default function HomePage() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <TrustStrip />
        <ComparisonTable />
        <HowItWorks />
        <ChatEntry />
        <FAQ />
      </main>
      <Footer />
    </>
  );
}
