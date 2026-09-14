"use client";

import { useEffect, useRef, useState } from "react";

export default function PaperStack() {
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div
      ref={sectionRef}
      className="absolute inset-0 flex items-center justify-center"
    >
      {/* Research Papers */}
      <div className="relative w-full h-full flex items-center justify-center">
        {/* Paper 01 */}
        <div
          className={`absolute w-64 h-80 bg-white rounded-lg border border-gray-200 p-5 transition-all duration-700 paper-texture ${
            isVisible ? "translate-x-0 opacity-100" : "-translate-x-20 opacity-0"
          }`}
          style={{
            transform: isVisible
              ? "rotate(-8deg) translate(-100px, -20px)"
              : "rotate(-8deg) translate(-120px, -20px)",
            boxShadow: "0 10px 30px -5px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1)",
          }}
        >
          <div className="space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[9px] font-mono text-gray-400">2023-04-15</span>
                <div className="text-[8px] text-gray-400 mt-0.5">arXiv:2304.xxxxx</div>
              </div>
              <div className="w-2.5 h-8 bg-lavender/40 rounded-sm shadow-sm"></div>
            </div>
            
            <h3 className="font-serif text-base leading-tight text-gray-900">
              Vision Transformers
              <br />
              for Medical Imaging
            </h3>
            
            <div className="text-[9px] text-gray-600">
              J. Smith, A. Chen et al.
            </div>

            <div className="pt-1">
              <div className="text-[8px] font-semibold text-gray-700 uppercase tracking-wide mb-1">
                Abstract
              </div>
              <div className="space-y-1">
                <div className="h-1 bg-gray-200 rounded w-full"></div>
                <div className="h-1 bg-gray-200 rounded w-[95%]"></div>
                <div className="h-1 bg-gray-200 rounded w-[90%]"></div>
              </div>
            </div>

            <div className="pt-1">
              <div className="text-[8px] font-semibold text-gray-700 uppercase tracking-wide mb-1">
                Methodology
              </div>
              <div className="space-y-1">
                <div className="h-1 bg-gray-200 rounded w-full"></div>
                <div className="h-1 bg-gray-200 rounded w-[88%]"></div>
                <div className="h-1 bg-gray-200 rounded w-[92%]"></div>
              </div>
            </div>

            <div className="w-full h-16 bg-gradient-to-br from-lavender/10 to-lavender/5 rounded border border-lavender/20 flex items-center justify-center">
              <svg
                className="w-10 h-10 text-lavender/40"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>

            <div className="text-right text-[8px] text-gray-400">
              Page 1
            </div>
          </div>
        </div>

        {/* Paper 02 - Center */}
        <div
          className={`absolute w-64 h-80 bg-white rounded-lg border border-gray-200 p-5 transition-all duration-700 delay-100 paper-texture ${
            isVisible ? "translate-y-0 opacity-100" : "translate-y-20 opacity-0"
          }`}
          style={{
            transform: isVisible ? "rotate(2deg)" : "rotate(2deg) translateY(20px)",
            zIndex: 10,
            boxShadow: "0 20px 40px -10px rgba(0, 0, 0, 0.25), 0 8px 16px -4px rgba(0, 0, 0, 0.15)",
          }}
        >
          <div className="space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[9px] font-mono text-gray-400">2023-06-22</span>
                <div className="text-[8px] text-gray-400 mt-0.5">arXiv:2306.xxxxx</div>
              </div>
              <div className="w-2.5 h-8 bg-light-blue/40 rounded-sm shadow-sm"></div>
            </div>
            
            <h3 className="font-serif text-base leading-tight text-gray-900">
              A Survey on
              <br />
              Self-Supervised Learning
            </h3>
            
            <div className="text-[9px] text-gray-600">
              M. Johnson, K. Lee et al.
            </div>

            <div className="pt-1">
              <div className="text-[8px] font-semibold text-gray-700 uppercase tracking-wide mb-1">
                Abstract
              </div>
              <div className="space-y-1">
                <div className="h-1 bg-gray-200 rounded w-full"></div>
                <div className="h-1 bg-gray-200 rounded w-[92%]"></div>
                <div className="h-1 bg-gray-200 rounded w-[96%]"></div>
              </div>
            </div>

            <div className="pt-1">
              <div className="text-[8px] font-semibold text-gray-700 uppercase tracking-wide mb-1">
                Methods
              </div>
              <div className="space-y-1">
                <div className="h-1 bg-gray-200 rounded w-full"></div>
                <div className="h-1 bg-gray-200 rounded w-[85%]"></div>
                <div className="h-1 bg-gray-200 rounded w-[90%]"></div>
                <div className="h-1 bg-gray-200 rounded w-[88%]"></div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-1.5">
              <div className="h-14 bg-gradient-to-t from-light-blue/30 to-light-blue/10 rounded border border-light-blue/30 relative">
                <div className="absolute bottom-0 left-0 right-0 h-[60%] bg-light-blue/40 rounded-b"></div>
              </div>
              <div className="h-14 bg-gradient-to-t from-light-blue/30 to-light-blue/10 rounded border border-light-blue/30 relative">
                <div className="absolute bottom-0 left-0 right-0 h-[80%] bg-light-blue/40 rounded-b"></div>
              </div>
              <div className="h-14 bg-gradient-to-t from-light-blue/30 to-light-blue/10 rounded border border-light-blue/30 relative">
                <div className="absolute bottom-0 left-0 right-0 h-[45%] bg-light-blue/40 rounded-b"></div>
              </div>
            </div>

            <div className="text-right text-[8px] text-gray-400">
              Page 3
            </div>
          </div>
        </div>

        {/* Paper 03 */}
        <div
          className={`absolute w-64 h-80 bg-white rounded-lg border border-gray-200 p-5 transition-all duration-700 delay-200 paper-texture ${
            isVisible ? "translate-x-0 opacity-100" : "translate-x-20 opacity-0"
          }`}
          style={{
            transform: isVisible
              ? "rotate(6deg) translate(100px, 30px)"
              : "rotate(6deg) translate(120px, 30px)",
            boxShadow: "0 10px 30px -5px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1)",
          }}
        >
          <div className="space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[9px] font-mono text-gray-400">2023-08-10</span>
                <div className="text-[8px] text-gray-400 mt-0.5">arXiv:2308.xxxxx</div>
              </div>
              <div className="w-2.5 h-8 bg-muted-rose/40 rounded-sm shadow-sm"></div>
            </div>
            
            <h3 className="font-serif text-base leading-tight text-gray-900">
              Efficient Models
              <br />
              for Edge Devices
            </h3>
            
            <div className="text-[9px] text-gray-600">
              R. Patel, S. Kim et al.
            </div>

            <div className="pt-1">
              <div className="text-[8px] font-semibold text-gray-700 uppercase tracking-wide mb-1">
                Abstract
              </div>
              <div className="space-y-1">
                <div className="h-1 bg-gray-200 rounded w-full"></div>
                <div className="h-1 bg-gray-200 rounded w-[90%]"></div>
                <div className="h-1 bg-gray-200 rounded w-[94%]"></div>
              </div>
            </div>

            <div className="pt-1">
              <div className="text-[8px] font-semibold text-gray-700 uppercase tracking-wide mb-1">
                Experiments
              </div>
              <div className="space-y-1">
                <div className="h-1 bg-gray-200 rounded w-full"></div>
                <div className="h-1 bg-gray-200 rounded w-[87%]"></div>
                <div className="h-1 bg-gray-200 rounded w-[91%]"></div>
              </div>
            </div>

            <div className="w-full h-16 bg-gradient-to-br from-muted-rose/10 to-muted-rose/5 rounded border border-muted-rose/20 relative overflow-hidden">
              <svg className="absolute inset-0 w-full h-full text-muted-rose/30" viewBox="0 0 100 60" preserveAspectRatio="none">
                <polyline
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  points="0,50 20,45 40,30 60,35 80,20 100,25"
                />
                <polyline
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeDasharray="3,3"
                  points="0,55 20,52 40,42 60,45 80,35 100,38"
                  opacity="0.6"
                />
              </svg>
            </div>

            <div className="text-right text-[8px] text-gray-400">
              Page 5
            </div>
          </div>
        </div>

        {/* Handwritten annotations */}
        <div
          className={`absolute text-sm italic text-gray-500 transition-opacity duration-1000 delay-300 ${
            isVisible ? "opacity-100" : "opacity-0"
          }`}
          style={{
            top: "15%",
            left: "-5%",
            transform: "rotate(-5deg)",
            fontFamily: "Brush Script MT, cursive",
          }}
        >
          Different approaches...
        </div>
        <div
          className={`absolute text-sm italic text-gray-500 transition-opacity duration-1000 delay-500 ${
            isVisible ? "opacity-100" : "opacity-0"
          }`}
          style={{
            bottom: "20%",
            left: "0%",
            transform: "rotate(-3deg)",
            fontFamily: "Brush Script MT, cursive",
          }}
        >
          Multiple datasets?
        </div>
        <div
          className={`absolute text-sm italic text-gray-500 transition-opacity duration-1000 delay-700 ${
            isVisible ? "opacity-100" : "opacity-0"
          }`}
          style={{
            top: "25%",
            right: "5%",
            transform: "rotate(4deg)",
            fontFamily: "Brush Script MT, cursive",
          }}
        >
          What's missing?
        </div>
      </div>
    </div>
  );
}
