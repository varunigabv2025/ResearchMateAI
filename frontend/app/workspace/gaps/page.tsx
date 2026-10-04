"use client";

import { useState } from "react";
import { analyzeGaps } from "@/lib/api/comparison";
import type { AnalyzeGapsResponse } from "@/lib/types/comparison";
import PaperSelector from "@/components/analysis/PaperSelector";
import GapAnalysisResults from "@/components/analysis/GapAnalysisResults";

export default function GapsPage() {
  const [selectedPaperIds, setSelectedPaperIds] = useState<string[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [gapResult, setGapResult] = useState<AnalyzeGapsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (selectedPaperIds.length < 2 || selectedPaperIds.length > 5) {
      setError("Please select 2-5 papers to analyze");
      return;
    }

    try {
      setIsAnalyzing(true);
      setError(null);
      const result = await analyzeGaps(selectedPaperIds);
      setGapResult(result);
    } catch (err) {
      console.error("Gap analysis failed:", err);
      setError(err instanceof Error ? err.message : "Gap analysis failed");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setGapResult(null);
    setSelectedPaperIds([]);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-serif text-3xl font-bold text-gray-900 mb-2">
            Research Gap Analysis
          </h1>
          <p className="text-gray-600">
            Identify potential research opportunities and contradictions across
            multiple papers
          </p>
        </div>

        {!gapResult ? (
          <>
            {/* Paper Selection */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
              <h2 className="font-serif text-xl font-semibold text-gray-900 mb-4">
                Select Papers
              </h2>
              <PaperSelector
                selectedPaperIds={selectedPaperIds}
                onSelectionChange={setSelectedPaperIds}
                minSelection={2}
                maxSelection={5}
              />
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 mb-6">
                <div className="flex items-start gap-3">
                  <svg
                    className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <div>
                    <h3 className="font-medium text-red-900 mb-1">
                      Analysis failed
                    </h3>
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Analyze Button */}
            <div className="flex justify-center">
              <button
                onClick={handleAnalyze}
                disabled={
                  isAnalyzing ||
                  selectedPaperIds.length < 2 ||
                  selectedPaperIds.length > 5
                }
                className={`
                  px-8 py-3 rounded-lg font-medium transition-all
                  ${
                    isAnalyzing ||
                    selectedPaperIds.length < 2 ||
                    selectedPaperIds.length > 5
                      ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                      : "bg-light-blue text-white hover:bg-light-blue/90 shadow-sm hover:shadow-md"
                  }
                `}
              >
                {isAnalyzing ? (
                  <span className="flex items-center gap-2">
                    <svg
                      className="animate-spin h-5 w-5"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Analyzing gaps...
                  </span>
                ) : (
                  <>Analyze Research Gaps</>
                )}
              </button>
            </div>
          </>
        ) : (
          <>
            {/* Gap Analysis Results */}
            <GapAnalysisResults result={gapResult} onReset={handleReset} />
          </>
        )}
      </div>
    </div>
  );
}
