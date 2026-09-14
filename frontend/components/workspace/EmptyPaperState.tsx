"use client";

interface EmptyPaperStateProps {
  onUploadClick?: () => void;
}

export default function EmptyPaperState({ onUploadClick }: EmptyPaperStateProps) {
  return (
    <div className="text-center py-16 px-4">
      <div className="max-w-md mx-auto">
        {/* Illustration */}
        <div className="mb-8 flex justify-center">
          <div className="relative">
            {/* Stack of papers illustration */}
            <div className="space-y-2">
              <div className="w-32 h-40 bg-gradient-to-br from-lavender/20 to-lavender/10 rounded-lg border border-lavender/30 shadow-sm transform rotate-[-8deg]"></div>
              <div className="w-32 h-40 bg-gradient-to-br from-light-blue/20 to-light-blue/10 rounded-lg border border-light-blue/30 shadow-md absolute top-0 left-8 transform rotate-[4deg]"></div>
              <div className="w-32 h-40 bg-gradient-to-br from-cream/80 to-cream/60 rounded-lg border-2 border-dashed border-gray-300 absolute top-0 left-16 flex items-center justify-center">
                <svg
                  className="w-12 h-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Text */}
        <h3 className="font-serif text-2xl text-gray-900 mb-3">
          Your research desk is empty
        </h3>
        <p className="text-gray-600 mb-8">
          Upload your first paper to begin analyzing, comparing, and discovering research gaps.
        </p>

        {/* Action */}
        {onUploadClick && (
          <button
            onClick={onUploadClick}
            className="inline-flex items-center gap-2 px-6 py-3 bg-light-blue text-white rounded-lg hover:bg-light-blue/90 transition-all hover:shadow-lg hover:-translate-y-0.5 font-medium"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            Upload Paper
          </button>
        )}
      </div>
    </div>
  );
}
