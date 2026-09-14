"use client";

import Link from "next/link";

export default function Hero() {
  return (
    <section className="min-h-[85vh] md:min-h-[90vh] flex items-center pt-20 pb-8 md:pt-24 md:pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto w-full">
        <div className="grid md:grid-cols-2 gap-8 lg:gap-12 items-center">
          {/* Left Column - Content */}
          <div className="space-y-6 animate-fade-in">
            <div>
              <p className="text-xs tracking-wider text-gray-600 uppercase mb-4">
                YOUR RESEARCH WORKSPACE
              </p>
              <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl leading-tight mb-5">
                Research is scattered.
                <br />
                <span className="text-lavender">Your understanding</span>
                <br />
                doesn't have to be.
              </h1>
              <p className="text-lg text-gray-700 leading-relaxed max-w-xl">
                Compare research papers, understand existing approaches, and
                surface possible research gaps — all in one place.
                <br />
                <br />
                With answers grounded in the original papers.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/workspace"
                className="group px-6 py-3.5 bg-light-blue text-white rounded-lg hover:bg-light-blue/90 transition-all hover:shadow-lg hover:-translate-y-0.5 flex items-center justify-center gap-2 font-medium"
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
              <button className="group px-6 py-3.5 border-2 border-gray-300 text-gray-700 rounded-lg hover:border-lavender hover:text-lavender transition-all flex items-center justify-center gap-2 font-medium">
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M8 5v14l11-7z" />
                </svg>
                See How It Works
              </button>
            </div>

            <div className="flex items-center gap-2 text-xs tracking-wider text-gray-500 uppercase pt-2">
              <span>UPLOAD</span>
              <span>•</span>
              <span>COMPARE</span>
              <span>•</span>
              <span>ANALYZE</span>
              <span>•</span>
              <span>DISCOVER POSSIBILITIES</span>
            </div>
          </div>

          {/* Right Column - Visual - will be filled by PaperStack component */}
          <div className="relative">
            {/* Placeholder for PaperStack component */}
            <div className="h-[400px] md:h-[500px]"></div>
          </div>
        </div>
      </div>
    </section>
  );
}
