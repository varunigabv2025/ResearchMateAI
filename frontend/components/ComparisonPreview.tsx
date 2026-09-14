"use client";

import { useEffect, useRef, useState } from "react";

export default function ComparisonPreview() {
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
      className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-8 relative z-10"
    >
      {/* Comparison Table Card */}
      <div
        className={`bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden transition-all duration-700 ${
          isVisible
            ? "translate-y-0 opacity-100"
            : "translate-y-10 opacity-0"
        }`}
      >
        <div className="bg-light-blue/10 px-6 py-4 border-b border-light-blue/20 flex items-center justify-between">
          <div>
            <h2 className="font-serif text-2xl text-gray-900">Comparison</h2>
            <p className="text-xs text-gray-600 mt-1">See key findings side by side</p>
          </div>
          <span className="text-xs font-semibold text-light-blue/70 uppercase tracking-wider">
            Sample Analysis
          </span>
        </div>
        
        {/* Desktop Table View */}
        <div className="hidden md:block overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Paper
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Method
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Dataset
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Result
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Limitation
                </th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                  Paper 01
                </td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-lavender/20 text-xs font-medium text-gray-700">
                    Vision Transformer
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-700">
                  NIH ChestX-ray14
                </td>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  94.2% accuracy
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  High computational cost
                </td>
              </tr>
              <tr className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                  Paper 02
                </td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-light-blue/20 text-xs font-medium text-gray-700">
                    Self-supervised
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-700">
                  ImageNet, CIFAR-10
                </td>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  Consistent improvement
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  Sensitive to pretraining
                </td>
              </tr>
              <tr className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                  Paper 03
                </td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-muted-rose/20 text-xs font-medium text-gray-700">
                    MobileNetV3
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-700">
                  ImageNet
                </td>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  75.2% top-1 accuracy
                </td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  Lower than larger models
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Mobile Stacked Cards View */}
        <div className="md:hidden divide-y divide-gray-200">
          {/* Paper 01 */}
          <div className="p-6 space-y-3">
            <div className="font-medium text-gray-900 text-sm">Paper 01</div>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-500 text-xs uppercase tracking-wider">Method:</span>
                <div className="mt-1">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-lavender/20 text-xs font-medium text-gray-700">
                    Vision Transformer
                  </span>
                </div>
              </div>
              <div>
                <span className="text-gray-500 text-xs uppercase tracking-wider">Dataset:</span>
                <div className="text-gray-700 mt-1">NIH ChestX-ray14</div>
              </div>
              <div>
                <span className="text-gray-500 text-xs uppercase tracking-wider">Result:</span>
                <div className="text-gray-900 font-medium mt-1">94.2% accuracy</div>
              </div>
              <div>
                <span className="text-gray-500 text-xs uppercase tracking-wider">Limitation:</span>
                <div className="text-gray-600 mt-1">High computational cost</div>
              </div>
            </div>
          </div>

          {/* Paper 02 */}
          <div className="p-6 space-y-3">
            <div className="font-medium text-gray-900 text-sm">Paper 02</div>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-500 text-xs uppercase tracking-wider">Method:</span>
                <div className="mt-1">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-light-blue/20 text-xs font-medium text-gray-700">
                    Self-supervised
                  </span>
                </div>
              </div>
              <div>
                <span className="text-gray-500 text-xs uppercase tracking-wider">Dataset:</span>
                <div className="text-gray-700 mt-1">ImageNet, CIFAR-10</div>
              </div>
              <div>
                <span className="text-gray-500 text-xs uppercase tracking-wider">Result:</span>
                <div className="text-gray-900 font-medium mt-1">Consistent improvement</div>
              </div>
              <div>
                <span className="text-gray-500 text-xs uppercase tracking-wider">Limitation:</span>
                <div className="text-gray-600 mt-1">Sensitive to pretraining</div>
              </div>
            </div>
          </div>

          {/* Paper 03 */}
          <div className="p-6 space-y-3">
            <div className="font-medium text-gray-900 text-sm">Paper 03</div>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-500 text-xs uppercase tracking-wider">Method:</span>
                <div className="mt-1">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-md bg-muted-rose/20 text-xs font-medium text-gray-700">
                    MobileNetV3
                  </span>
                </div>
              </div>
              <div>
                <span className="text-gray-500 text-xs uppercase tracking-wider">Dataset:</span>
                <div className="text-gray-700 mt-1">ImageNet</div>
              </div>
              <div>
                <span className="text-gray-500 text-xs uppercase tracking-wider">Result:</span>
                <div className="text-gray-900 font-medium mt-1">75.2% top-1 accuracy</div>
              </div>
              <div>
                <span className="text-gray-500 text-xs uppercase tracking-wider">Limitation:</span>
                <div className="text-gray-600 mt-1">Lower than larger models</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Arrow connector to gaps */}
      <div className="flex justify-center py-8">
        <div className="flex flex-col items-center gap-2">
          <svg
            className="w-6 h-6 text-muted-rose/60 animate-bounce"
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
          <span className="text-xs text-gray-500 uppercase tracking-wider">Discover</span>
        </div>
      </div>
    </div>
  );
}
