"use client";

import type { Paper } from "@/lib/types/paper";

interface PaperCardProps {
  paper: Paper;
  selected?: boolean;
  onSelect?: (paperId: string) => void;
  onDelete?: (paperId: string) => void;
  onAskQuestion?: (paperId: string) => void;
}

export default function PaperCard({
  paper,
  selected = false,
  onSelect,
  onDelete,
  onAskQuestion,
}: PaperCardProps) {
  const displayName = paper.original_filename || paper.filename;
  const hasError = !paper.processed && paper.processing_error;

  return (
    <div
      className={`relative bg-white rounded-xl border-2 transition-all hover:shadow-lg ${
        selected
          ? "border-light-blue shadow-md"
          : hasError
          ? "border-red-200"
          : "border-gray-200 hover:border-gray-300"
      }`}
    >
      <div className="p-6">
        {/* Selection Checkbox */}
        {onSelect && (
          <div className="flex items-start justify-between mb-4">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onSelect(paper.id);
              }}
              className="flex items-center gap-2 cursor-pointer group"
            >
              <div
                className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                  selected
                    ? "bg-light-blue border-light-blue"
                    : "border-gray-300 group-hover:border-light-blue"
                }`}
              >
                {selected && (
                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </div>
              <span className="text-sm text-gray-600">
                {selected ? "Selected" : "Select"}
              </span>
            </button>

            {/* Delete Button */}
            {onDelete && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(paper.id);
                }}
                className="text-gray-400 hover:text-red-600 transition-colors p-1"
                title="Delete paper"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </button>
            )}
          </div>
        )}

        {/* Paper Icon */}
        <div className="flex items-center justify-center w-16 h-16 rounded-lg bg-light-blue/10 mb-4">
          <svg
            className="w-8 h-8 text-light-blue"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>

        {/* Paper Title */}
        <h3 className="font-serif text-lg text-gray-900 mb-3 line-clamp-2" title={displayName}>
          {displayName}
        </h3>

        {/* Paper Metadata */}
        {paper.processed && !hasError && (
          <div className="space-y-2 mb-4">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
              <span>{paper.page_count} pages</span>
            </div>
          </div>
        )}

        {/* Processing Error */}
        {hasError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">Processing failed</p>
            {paper.processing_error && (
              <p className="text-xs text-red-500 mt-1">{paper.processing_error}</p>
            )}
          </div>
        )}

        {/* Status Badge */}
        <div className="mb-4">
          {paper.processed && !hasError ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-100 text-green-700 text-xs font-medium">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              Ready
            </span>
          ) : hasError ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-100 text-red-700 text-xs font-medium">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              Error
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-lavender/20 text-lavender text-xs font-medium">
              <svg className="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Processing
            </span>
          )}
        </div>

        {/* Actions */}
        {paper.processed && !hasError && onAskQuestion && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onAskQuestion(paper.id);
            }}
            className="w-full px-4 py-2.5 bg-light-blue text-white rounded-lg hover:bg-light-blue/90 transition-all font-medium text-sm relative z-10"
          >
            Ask Questions
          </button>
        )}
      </div>
    </div>
  );
}
