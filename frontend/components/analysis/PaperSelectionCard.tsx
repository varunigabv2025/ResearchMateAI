"use client";

import type { Paper } from "@/lib/types/paper";

interface PaperSelectionCardProps {
  paper: Paper;
  selected: boolean;
  onToggle: () => void;
  disabled?: boolean;
}

export default function PaperSelectionCard({
  paper,
  selected,
  onToggle,
  disabled = false,
}: PaperSelectionCardProps) {
  const handleClick = () => {
    if (!disabled) {
      onToggle();
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled}
      className={`
        w-full text-left p-4 rounded-lg border-2 transition-all
        ${
          selected
            ? "border-light-blue bg-light-blue/10"
            : "border-gray-200 bg-white hover:border-gray-300"
        }
        ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
      `}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            {selected && (
              <svg
                className="w-5 h-5 text-light-blue flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            )}
            <h3 className="font-medium text-gray-900 truncate">
              {paper.original_filename}
            </h3>
          </div>

          <div className="text-sm text-gray-600 space-y-1">
            <div className="flex items-center gap-2">
              <svg
                className="w-4 h-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
              <span>{paper.page_count} pages</span>
            </div>

            {paper.processed ? (
              <div className="flex items-center gap-2 text-green-600">
                <svg
                  className="w-4 h-4"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>Ready</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-amber-600">
                <svg
                  className="w-4 h-4 animate-spin"
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
                <span>Processing</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </button>
  );
}
