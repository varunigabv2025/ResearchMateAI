"use client";

import Link from "next/link";

export default function ClosingSection() {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-cream/50 to-lavender/10">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          {/* Echo of hero messaging */}
          <p className="text-xs tracking-wider text-gray-600 uppercase mb-4">
            The Final Step
          </p>
          <h2 className="font-serif text-4xl sm:text-5xl lg:text-6xl leading-tight mb-6 text-gray-900">
            Not just another PDF reader.
          </h2>
          <p className="font-serif text-3xl sm:text-4xl text-lavender mb-6">
            A research partner for what's next.
          </p>
          <p className="text-lg text-gray-700 max-w-2xl mx-auto mb-10">
            ResearchMate helps you move from scattered papers to structured insight.
          </p>

          <Link
            href="/workspace"
            className="inline-flex items-center gap-2 px-8 py-4 bg-light-blue text-white rounded-lg hover:bg-light-blue/90 transition-all hover:shadow-lg hover:-translate-y-0.5 font-medium text-lg group"
          >
            Start Researching
            <svg
              className="w-5 h-5 group-hover:translate-x-1 transition-transform"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </Link>
        </div>

        {/* Stacked research layers illustration */}
        <div className="flex justify-center mt-16">
          <div className="relative">
            <div className="space-y-2">
              <div className="w-48 sm:w-56 h-16 bg-gradient-to-r from-lavender/30 to-lavender/20 rounded-lg border border-lavender/40 flex items-center justify-center shadow-md transform hover:scale-105 transition-transform">
                <span className="font-serif text-base sm:text-lg font-medium text-gray-800">IDEAS</span>
              </div>
              <div className="w-52 sm:w-60 h-16 bg-gradient-to-r from-light-blue/30 to-light-blue/20 rounded-lg border border-light-blue/40 flex items-center justify-center shadow-lg transform translate-x-4 sm:translate-x-8 hover:scale-105 transition-transform">
                <span className="font-serif text-base sm:text-lg font-medium text-gray-800">PAPERS</span>
              </div>
              <div className="w-56 sm:w-64 h-16 bg-gradient-to-r from-lavender/25 to-lavender/15 rounded-lg border border-lavender/35 flex items-center justify-center shadow-md transform -translate-x-2 hover:scale-105 transition-transform">
                <span className="font-serif text-base sm:text-lg font-medium text-gray-800">INSIGHTS</span>
              </div>
              <div className="w-60 sm:w-72 h-16 bg-gradient-to-r from-light-blue/25 to-light-blue/15 rounded-lg border border-light-blue/35 flex items-center justify-center shadow-lg transform translate-x-6 sm:translate-x-12 hover:scale-105 transition-transform">
                <span className="font-serif text-base sm:text-lg font-medium text-gray-800">POSSIBILITIES</span>
              </div>
            </div>

            {/* Decorative handwritten note */}
            <div className="absolute -right-16 sm:-right-24 top-8 text-sm italic text-gray-500 hidden lg:block">
              <p style={{ fontFamily: "Brush Script MT, cursive" }}>
                From papers
                <br />
                to possibilities
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
