"use client";

export default function QAEmptyState() {
  return (
    <div className="text-center py-12 px-4">
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
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
      </div>
      
      <h3 className="font-serif text-xl text-gray-900 mb-2">
        Ask about this paper
      </h3>
      
      <p className="text-gray-600 mb-6 max-w-md mx-auto">
        Get grounded answers from the paper's content with citations to specific pages and sections.
      </p>
      
      <div className="max-w-md mx-auto text-left">
        <p className="text-sm font-medium text-gray-700 mb-2">Example questions:</p>
        <ul className="space-y-1 text-sm text-gray-600">
          <li className="flex items-start gap-2">
            <span className="text-light-blue mt-1">•</span>
            <span>What methodology was used in this study?</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-light-blue mt-1">•</span>
            <span>What were the main findings?</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-light-blue mt-1">•</span>
            <span>What dataset was used for evaluation?</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-light-blue mt-1">•</span>
            <span>What limitations does the paper acknowledge?</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
