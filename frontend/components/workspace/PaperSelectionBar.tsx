"use client";

import { config } from "@/lib/config";

interface PaperSelectionBarProps {
  selectedCount: number;
  onCompare?: () => void;
  onClear?: () => void;
}

export default function PaperSelectionBar({
  selectedCount,
  onCompare,
  onClear,
}: PaperSelectionBarProps) {
  if (selectedCount === 0) return null;

  const canCompare =
    selectedCount >= config.minPapersForComparison &&
    selectedCount <= config.maxPapersForComparison;

  return (
    <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50 animate-fade-in">
      <div className="bg-white shadow-2xl rounded-xl border-2 border-light-blue/20 px-6 py-4 flex items-center gap-6">
        {/* Selection Info */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-light-blue/15 flex items-center justify-center">
            <span className="text-sm font-bold text-light-blue">{selectedCount}</span>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">
              {selectedCount} {selectedCount === 1 ? "paper" : "papers"} selected
            </p>
            {!canCompare && (
              <p className="text-xs text-gray-500">
                {selectedCount < config.minPapersForComparison
                  ? `Select at least ${config.minPapersForComparison} papers to compare`
                  : `Maximum ${config.maxPapersForComparison} papers allowed`}
              </p>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 border-l border-gray-200 pl-6">
          {onClear && (
            <button
              onClick={onClear}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 font-medium transition-colors"
            >
              Clear
            </button>
          )}

          {onCompare && (
            <button
              onClick={onCompare}
              disabled={!canCompare}
              className={`px-6 py-2.5 rounded-lg font-medium text-sm transition-all flex items-center gap-2 ${
                canCompare
                  ? "bg-light-blue text-white hover:bg-light-blue/90 hover:shadow-md"
                  : "bg-gray-200 text-gray-400 cursor-not-allowed"
              }`}
            >
              Compare Papers
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
