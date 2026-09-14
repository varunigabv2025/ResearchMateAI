"use client";

import { useEffect, useRef, useState } from "react";

export default function ResearchGapCard() {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={sectionRef}
      className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-12"
    >
      <div
        className={`bg-white rounded-2xl shadow-xl border-2 border-muted-rose/30 overflow-hidden transition-all duration-700 delay-200 ${
          isVisible
            ? "translate-y-0 opacity-100"
            : "translate-y-10 opacity-0"
        }`}
      >
        <div className="bg-muted-rose/10 px-6 py-4 border-b border-muted-rose/20">
          <div className="flex items-center justify-between">
            <h2 className="font-serif text-2xl text-gray-900">
              Possible Research Gaps
            </h2>
            <div className="flex items-center gap-2 text-xs text-muted-rose font-semibold">
              <svg
                className="w-4 h-4"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
              AI-SUGGESTED
            </div>
          </div>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-muted-rose rounded-full mt-2"></div>
            <p className="text-gray-700 leading-relaxed">
              Limited dataset diversity across studies
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-muted-rose rounded-full mt-2"></div>
            <p className="text-gray-700 leading-relaxed">
              Lack of direct comparison under common settings
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-muted-rose rounded-full mt-2"></div>
            <p className="text-gray-700 leading-relaxed">
              Unexplored efficiency–performance trade-offs
            </p>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 italic">
              Verify against the literature yourself.
            </p>
          </div>
        </div>
      </div>

      {/* Handwritten annotation */}
      <div
        className={`relative mt-6 ml-8 transition-opacity duration-1000 delay-500 ${
          isVisible ? "opacity-100" : "opacity-0"
        }`}
      >
        <p
          className="text-sm italic text-gray-500"
          style={{
            fontFamily: "Brush Script MT, cursive",
            transform: "rotate(-2deg)",
          }}
        >
          New possibilities
          <br />
          for research!
        </p>
        <svg
          className="absolute -left-8 top-0 w-12 h-12 text-gray-400"
          fill="none"
          stroke="currentColor"
          strokeWidth="1"
          viewBox="0 0 24 24"
        >
          <path d="M3 12 Q8 8, 12 12" />
        </svg>
      </div>
    </div>
  );
}
