import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import PaperStack from "@/components/PaperStack";
import ComparisonPreview from "@/components/ComparisonPreview";
import ResearchGapCard from "@/components/ResearchGapCard";
import FeatureCards from "@/components/FeatureCards";
import HowItWorks from "@/components/HowItWorks";
import ClosingSection from "@/components/ClosingSection";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="min-h-screen">
      <Navbar />

      {/* Hero Section with Paper Stack */}
      <div className="relative overflow-hidden">
        <Hero />
        {/* Paper Stack positioned absolutely within Hero */}
        <div className="absolute top-20 md:top-24 right-0 w-1/2 h-[400px] md:h-[500px] pointer-events-none hidden md:block">
          <PaperStack />
        </div>
      </div>

      {/* Mobile Paper Stack */}
      <div className="md:hidden px-4 pb-8">
        <div className="relative h-[400px]">
          <PaperStack />
        </div>
      </div>

      {/* Visual Flow Connector - Papers to Comparison */}
      <div className="flex justify-center py-8 md:py-12">
        <div className="flex flex-col items-center gap-2">
          <svg
            className="w-6 h-6 text-light-blue/60 animate-bounce"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 14l-7 7m0 0l-7-7m7 7V3"
            />
          </svg>
          <span className="text-xs text-gray-500 uppercase tracking-wider">Compare</span>
        </div>
      </div>

      {/* Comparison and Gap Cards */}
      <ComparisonPreview />
      <ResearchGapCard />

      {/* Features */}
      <FeatureCards />

      {/* How It Works */}
      <HowItWorks />

      {/* Closing CTA */}
      <ClosingSection />

      {/* Footer */}
      <Footer />
    </main>
  );
}
