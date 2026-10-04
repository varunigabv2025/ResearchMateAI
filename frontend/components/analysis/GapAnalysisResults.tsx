"use client";

import type { AnalyzeGapsResponse } from "@/lib/types/comparison";

interface GapAnalysisResultsProps {
  result: AnalyzeGapsResponse;
  onReset: () => void;
}

export default function GapAnalysisResults({
  result,
  onReset,
}: GapAnalysisResultsProps) {
  const { gaps, disclaimer } = result;

  return (
    <div>
      {/* Header with Reset Button */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="font-serif text-2xl font-bold text-gray-900 mb-1">
            Research Gap Analysis
          </h2>
          <p className="text-gray-600">
            {gaps.length === 0
              ? "No significant gaps identified"
              : `${gaps.length} potential research ${
                  gaps.length === 1 ? "gap" : "gaps"
                } identified`}
          </p>
        </div>
        <button
          onClick={onReset}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          New Analysis
        </button>
      </div>

      {/* Disclaimer */}
      <div className="mb-6 bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <svg
            className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-sm text-amber-800">
            <span className="font-semibold">Notice:</span> {disclaimer}
          </p>
        </div>
      </div>

      {/* Gap Cards */}
      {gaps.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
            <svg
              className="w-8 h-8 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h3 className="font-serif text-xl text-gray-900 mb-2">
            No significant gaps identified
          </h3>
          <p className="text-gray-600 max-w-md mx-auto">
            The analysis did not identify major research gaps or contradictions
            in the selected papers. This could indicate well-aligned research
            directions.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {gaps.map((gap, index) => (
            <div
              key={index}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6"
            >
              {/* Gap Header */}
              <div className="flex items-start gap-3 mb-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-light-blue/10 flex items-center justify-center">
                  <span className="text-sm font-semibold text-light-blue">
                    {index + 1}
                  </span>
                </div>
                <div className="flex-1">
                  <h3 className="font-serif text-lg font-semibold text-gray-900">
                    {gap.title}
                  </h3>
                </div>
              </div>

              {/* Gap Description */}
              <div className="mb-4 pl-11">
                <p className="text-gray-700 leading-relaxed">
                  {gap.description}
                </p>
              </div>

              {/* Evidence/Basis */}
              <div className="pl-11">
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                  <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                    Evidence & Basis
                  </h4>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    {gap.basis}
                  </p>
                </div>
              </div>

              {/* Inference Notice */}
              <div className="mt-4 pl-11">
                <div className="flex items-start gap-2">
                  <svg
                    className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <p className="text-xs text-blue-700">
                    This is an AI inference from the analyzed literature.
                    Verify against additional sources before proceeding.
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
