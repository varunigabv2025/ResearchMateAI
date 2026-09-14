"use client";

import type { Paper } from "@/lib/types/paper";

interface ActivePaperHeaderProps {
  paper: Paper;
}

export default function ActivePaperHeader({ paper }: ActivePaperHeaderProps) {
  return (
    <div className="mb-6 bg-white rounded-lg border-2 border-gray-200 p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-light-blue/10 flex items-center justify-center flex-shrink-0">
              <svg
                className="w-5 h-5 text-light-blue"
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
            <div>
              <h2 className="font-serif text-2xl text-gray-900">
                {paper.original_filename}
              </h2>
              <div className="flex items-center gap-4 mt-1">
                <span className="text-sm text-gray-600">
                  {paper.page_count} {paper.page_count === 1 ? 'page' : 'pages'}
                </span>
                {paper.processed && (
                  <span className="inline-flex items-center gap-1.5 text-sm text-green-700">
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
                    Ready
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-sm text-gray-600">
          Ask questions about this paper's methodology, results, or findings. 
          Answers are grounded in the paper's actual content with citations.
        </p>
      </div>
    </div>
  );
}
