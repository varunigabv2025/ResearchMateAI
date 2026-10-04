"use client";

import type { SourceCitation } from "@/lib/types/paper";

interface AnswerMessageProps {
  answer: string;
  sources: SourceCitation[];
}

export default function AnswerMessage({ answer, sources }: AnswerMessageProps) {
  return (
    <div className="flex gap-4 mb-6">
      <div className="w-8 h-8 rounded-full bg-light-blue flex items-center justify-center flex-shrink-0">
        <svg
          className="w-4 h-4 text-white"
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
      
      <div className="flex-1">
        <div className="text-sm font-medium text-gray-900 mb-1">ResearchMate</div>
        
        <div className="text-gray-900 whitespace-pre-wrap mb-4 leading-relaxed">
          {answer}
        </div>
        
        {sources && sources.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="text-sm font-medium text-gray-700 mb-2">
              Sources ({sources.length})
            </div>
            <div className="space-y-2">
              {sources.map((source, idx) => (
                <div
                  key={source.chunk_id}
                  className="flex items-start gap-2 text-sm text-gray-600 bg-gray-50 rounded-lg p-3"
                >
                  <span className="font-medium text-gray-900 flex-shrink-0">
                    [{idx + 1}]
                  </span>
                  <div className="flex-1">
                    <span className="font-medium">Page {source.page_number}</span>
                    {source.section && (
                      <span className="text-gray-500"> · {source.section}</span>
                    )}
                    <span className="text-gray-400 ml-2">
                      (relevance: {(source.similarity * 100).toFixed(0)}%)
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
