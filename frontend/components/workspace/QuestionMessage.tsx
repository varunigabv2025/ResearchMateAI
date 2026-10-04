"use client";

interface QuestionMessageProps {
  question: string;
}

export default function QuestionMessage({ question }: QuestionMessageProps) {
  return (
    <div className="flex gap-4 mb-6">
      <div className="w-8 h-8 rounded-full bg-gray-900 flex items-center justify-center flex-shrink-0">
        <svg
          className="w-4 h-4 text-white"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fillRule="evenodd"
            d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
            clipRule="evenodd"
          />
        </svg>
      </div>
      
      <div className="flex-1">
        <div className="text-sm font-medium text-gray-900 mb-1">You</div>
        <div className="text-gray-900 whitespace-pre-wrap">{question}</div>
      </div>
    </div>
  );
}
