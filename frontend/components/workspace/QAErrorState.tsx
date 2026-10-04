"use client";

interface QAErrorStateProps {
  error: string;
  onRetry?: () => void;
}

export default function QAErrorState({ error, onRetry }: QAErrorStateProps) {
  return (
    <div className="text-center py-12 px-4">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-4">
        <svg
          className="w-8 h-8 text-red-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      
      <h3 className="font-serif text-xl text-gray-900 mb-2">
        Unable to get answer
      </h3>
      
      <p className="text-gray-600 mb-6 max-w-md mx-auto">
        {error}
      </p>
      
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-6 py-2.5 bg-light-blue text-white rounded-lg font-medium hover:bg-light-blue/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-light-blue transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
}
