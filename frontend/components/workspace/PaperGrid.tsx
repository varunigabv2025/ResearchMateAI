"use client";

import type { Paper } from "@/lib/types/paper";
import PaperCard from "./PaperCard";
import EmptyPaperState from "./EmptyPaperState";

interface PaperGridProps {
  papers: Paper[];
  selectedPaperIds: string[];
  onSelectPaper?: (paperId: string) => void;
  onDeletePaper?: (paperId: string) => void;
  onAskQuestion?: (paperId: string) => void;
  onUploadClick?: () => void;
  isLoading?: boolean;
}

export default function PaperGrid({
  papers,
  selectedPaperIds,
  onSelectPaper,
  onDeletePaper,
  onAskQuestion,
  onUploadClick,
  isLoading = false,
}: PaperGridProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-center">
          <svg
            className="animate-spin h-8 w-8 text-light-blue mx-auto mb-4"
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
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <p className="text-gray-600">Loading papers...</p>
        </div>
      </div>
    );
  }

  if (papers.length === 0) {
    return <EmptyPaperState onUploadClick={onUploadClick} />;
  }

  return (
    <div>
      {/* Paper Count */}
      <div className="mb-6">
        <p className="text-sm text-gray-600">
          {papers.length} {papers.length === 1 ? "paper" : "papers"}
        </p>
      </div>

      {/* Paper Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {papers.map((paper) => (
          <PaperCard
            key={paper.id}
            paper={paper}
            selected={selectedPaperIds.includes(paper.id)}
            onSelect={onSelectPaper}
            onDelete={onDeletePaper}
            onAskQuestion={onAskQuestion}
          />
        ))}
      </div>
    </div>
  );
}
