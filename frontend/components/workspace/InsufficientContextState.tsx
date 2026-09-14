"use client";

interface InsufficientContextStateProps {
  question: string;
}

export default function InsufficientContextState({
  question,
}: InsufficientContextStateProps) {
  return (
    <div className="bg-amber-50 border-2 border-amber-200 rounded-lg p-6 my-6">
      <div className="flex gap-4">
        <div className="flex-shrink-0">
          <svg
            className="w-6 h-6 text-amber-600"
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
        </div>
        
        <div className="flex-1">
          <h3 className="font-medium text-amber-900 mb-2">
            Insufficient context to answer
          </h3>
          
          <p className="text-amber-800 mb-3">
            The paper doesn't contain enough relevant information to confidently answer this question:
          </p>
          
          <div className="bg-white border border-amber-200 rounded-lg p-3 mb-3">
            <p className="text-gray-700 italic">"{question}"</p>
          </div>
          
          <p className="text-sm text-amber-700">
            Try rephrasing your question to focus on topics explicitly covered in the paper, 
            or ask about different aspects of the research.
          </p>
        </div>
      </div>
    </div>
  );
}
