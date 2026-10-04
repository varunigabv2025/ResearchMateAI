"use client";

import { useEffect, useState } from "react";
import { listPapers } from "@/lib/api/papers";
import type { Paper } from "@/lib/types/paper";
import PaperSelectionCard from "./PaperSelectionCard";

interface PaperSelectorProps {
  selectedPaperIds: string[];
  onSelectionChange: (paperIds: string[]) => void;
  minSelection?: number;
  maxSelection?: number;
}

export default function PaperSelector({
  selectedPaperIds,
  onSelectionChange,
  minSelection = 2,
  maxSelection = 5,
}: PaperSelectorProps) {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPapers = async () => {
      try {
        setLoading(true);
        setError(null);
        const allPapers = await listPapers();
        // Only show processed papers
        const processedPapers = allPapers.filter((p) => p.processed);
        setPapers(processedPapers);
      } catch (err) {
        console.error("Failed to load papers:", err);
        setError("Failed to load papers");
      } finally {
        setLoading(false);
      }
    };

    loadPapers();
  }, []);

  const handleToggle = (paperId: string) => {
    if (selectedPaperIds.includes(paperId)) {
      onSelectionChange(selectedPaperIds.filter((id) => id !== paperId));
    } else {
      if (selectedPaperIds.length < maxSelection) {
        onSelectionChange([...selectedPaperIds, paperId]);
      }
    }
  };

  const isDisabled = (paperId: string) => {
    return (
      !selectedPaperIds.includes(paperId) &&
      selectedPaperIds.length >= maxSelection
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-light-blue/10 mb-4">
            <svg
              className="animate-spin h-6 w-6 text-light-blue"
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
          </div>
          <p className="text-gray-600">Loading papers...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6">
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
              Unable to load papers
            </h3>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (papers.length === 0) {
    return (
      <div className="text-center py-12 px-4 bg-gray-50 rounded-lg">
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
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <h3 className="font-serif text-xl text-gray-900 mb-2">
          No papers uploaded yet
        </h3>
        <p className="text-gray-600">
          Upload and process at least {minSelection} papers to use this feature
        </p>
      </div>
    );
  }

  if (papers.length < minSelection) {
    return (
      <div className="bg-amber-50 border-2 border-amber-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <svg
            className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5"
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
          <div>
            <h3 className="font-medium text-amber-900 mb-1">
              More papers needed
            </h3>
            <p className="text-sm text-amber-700">
              You have {papers.length} processed {papers.length === 1 ? "paper" : "papers"}.
              At least {minSelection} papers are required for analysis.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600">
            {selectedPaperIds.length === 0 ? (
              <>Select {minSelection}–{maxSelection} papers to compare</>
            ) : (
              <>
                {selectedPaperIds.length} of {maxSelection} selected
              </>
            )}
          </p>
          {selectedPaperIds.length > 0 && (
            <button
              onClick={() => onSelectionChange([])}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Clear selection
            </button>
          )}
        </div>
      </div>

      <div className="grid gap-3">
        {papers.map((paper) => (
          <PaperSelectionCard
            key={paper.id}
            paper={paper}
            selected={selectedPaperIds.includes(paper.id)}
            onToggle={() => handleToggle(paper.id)}
            disabled={isDisabled(paper.id)}
          />
        ))}
      </div>
    </div>
  );
}
