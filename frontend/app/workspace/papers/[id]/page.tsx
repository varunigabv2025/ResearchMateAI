"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import WorkspaceShell from "@/components/workspace/WorkspaceShell";
import ActivePaperHeader from "@/components/workspace/ActivePaperHeader";
import QuestionComposer from "@/components/workspace/QuestionComposer";
import ConversationThread from "@/components/workspace/ConversationThread";
import QALoadingState from "@/components/workspace/QALoadingState";
import QAEmptyState from "@/components/workspace/QAEmptyState";
import QAErrorState from "@/components/workspace/QAErrorState";
import InsufficientContextState from "@/components/workspace/InsufficientContextState";
import { listPapers } from "@/lib/api/papers";
import { askQuestion } from "@/lib/api/qa";
import type { Paper, QuestionResponse } from "@/lib/types/paper";

interface ConversationEntry {
  question: string;
  response: QuestionResponse;
}

export default function PaperDetailPage() {
  const params = useParams();
  const paperId = params.id as string;

  const [paper, setPaper] = useState<Paper | null>(null);
  const [isPaperLoading, setIsPaperLoading] = useState(true);
  const [paperError, setPaperError] = useState<string | null>(null);

  const [conversation, setConversation] = useState<ConversationEntry[]>([]);
  const [isAsking, setIsAsking] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState<string | null>(null);
  const [askError, setAskError] = useState<string | null>(null);
  const [retryQuestion, setRetryQuestion] = useState<string | null>(null);

  // Load paper details
  useEffect(() => {
    const loadPaper = async () => {
      try {
        setIsPaperLoading(true);
        setPaperError(null);
        const papers = await listPapers();
        const foundPaper = papers.find((p) => p.id === paperId);
        
        if (!foundPaper) {
          setPaperError("Paper not found");
        } else if (!foundPaper.processed) {
          setPaperError(
            foundPaper.processing_error
              ? `Paper processing failed: ${foundPaper.processing_error}`
              : "Paper is still being processed. Please wait."
          );
        } else {
          setPaper(foundPaper);
        }
      } catch (error) {
        console.error("Failed to load paper:", error);
        setPaperError("Unable to load paper details");
      } finally {
        setIsPaperLoading(false);
      }
    };

    loadPaper();
  }, [paperId]);

  // Handle question submission
  const handleAskQuestion = useCallback(
    async (question: string) => {
      if (!paper || isAsking) return;

      setCurrentQuestion(question);
      setIsAsking(true);
      setAskError(null);
      setRetryQuestion(null);

      try {
        const response = await askQuestion(paperId, question);
        
        // Add to conversation
        setConversation((prev) => [
          ...prev,
          { question, response },
        ]);
        setCurrentQuestion(null);
      } catch (error) {
        console.error("Failed to get answer:", error);
        const errorMessage =
          error instanceof Error
            ? error.message
            : "Unable to get an answer. Please try again.";
        setAskError(errorMessage);
        setRetryQuestion(question);
      } finally {
        setIsAsking(false);
      }
    },
    [paper, paperId, isAsking]
  );

  // Handle retry
  const handleRetry = useCallback(() => {
    if (retryQuestion) {
      handleAskQuestion(retryQuestion);
    }
  }, [retryQuestion, handleAskQuestion]);

  // Get the last response for rendering insufficient context state
  const lastEntry = conversation[conversation.length - 1];
  const showInsufficientContext =
    lastEntry && !lastEntry.response.has_sufficient_context;

  // Loading state
  if (isPaperLoading) {
    return (
      <WorkspaceShell>
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center gap-3">
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
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            <span className="text-gray-600">Loading paper...</span>
          </div>
        </div>
      </WorkspaceShell>
    );
  }

  // Error state
  if (paperError || !paper) {
    return (
      <WorkspaceShell>
        <div className="bg-white rounded-xl border-2 border-red-200 p-8">
          <div className="max-w-md mx-auto text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <h3 className="font-serif text-2xl text-gray-900 mb-3">Unable to Load Paper</h3>
            <p className="text-gray-600 mb-4">{paperError || "Paper not found"}</p>
            <a
              href="/workspace"
              className="inline-block px-4 py-2 bg-light-blue text-white rounded-lg hover:bg-light-blue/90 transition-colors"
            >
              Back to Workspace
            </a>
          </div>
        </div>
      </WorkspaceShell>
    );
  }

  return (
    <WorkspaceShell>
      {/* Active Paper */}
      <ActivePaperHeader paper={paper} />

      {/* Question Composer */}
      <QuestionComposer
        onSubmit={handleAskQuestion}
        isLoading={isAsking}
        disabled={!paper.processed}
      />

      {/* Conversation Thread */}
      {conversation.length > 0 && (
        <ConversationThread conversation={conversation} />
      )}

      {/* Loading State */}
      {isAsking && currentQuestion && <QALoadingState />}

      {/* Error State */}
      {askError && <QAErrorState error={askError} onRetry={handleRetry} />}

      {/* Insufficient Context State */}
      {showInsufficientContext && !isAsking && (
        <InsufficientContextState question={lastEntry.question} />
      )}
    </WorkspaceShell>
  );
}
