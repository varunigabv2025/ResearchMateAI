"use client";

import { useState, useCallback, FormEvent, KeyboardEvent } from "react";

interface QuestionComposerProps {
  onSubmit: (question: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export default function QuestionComposer({
  onSubmit,
  isLoading = false,
  disabled = false,
}: QuestionComposerProps) {
  const [question, setQuestion] = useState("");

  const handleSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      const trimmedQuestion = question.trim();
      if (trimmedQuestion && !isLoading && !disabled) {
        onSubmit(trimmedQuestion);
        setQuestion("");
      }
    },
    [question, onSubmit, isLoading, disabled]
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      // Submit on Enter (without Shift)
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit(e as any);
      }
    },
    [handleSubmit]
  );

  const isSubmitDisabled = !question.trim() || isLoading || disabled;

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg border-2 border-gray-200 p-4">
      <label htmlFor="question-input" className="sr-only">
        Ask a question about this paper
      </label>
      
      <textarea
        id="question-input"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isLoading || disabled}
        placeholder="Ask about methodology, results, findings..."
        className="w-full px-4 py-3 text-gray-900 placeholder-gray-400 border border-gray-300 rounded-lg focus:ring-2 focus:ring-light-blue focus:border-transparent resize-none disabled:bg-gray-50 disabled:text-gray-500"
        rows={3}
        aria-label="Question input"
        aria-describedby="question-hint"
      />
      
      <div className="flex items-center justify-between mt-3">
        <p id="question-hint" className="text-sm text-gray-500">
          {isLoading ? "Getting answer..." : "Press Enter to submit, Shift+Enter for new line"}
        </p>
        
        <button
          type="submit"
          disabled={isSubmitDisabled}
          className="px-6 py-2.5 bg-light-blue text-white rounded-lg font-medium hover:bg-light-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-light-blue disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          aria-label="Submit question"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <svg
                className="animate-spin h-4 w-4"
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
              Asking...
            </span>
          ) : (
            "Ask Question"
          )}
        </button>
      </div>
    </form>
  );
}
