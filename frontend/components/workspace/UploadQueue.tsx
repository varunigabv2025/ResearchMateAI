"use client";

import type { UploadProgress } from "@/lib/types/paper";

interface UploadQueueProps {
  uploads: UploadProgress[];
}

export default function UploadQueue({ uploads }: UploadQueueProps) {
  if (uploads.length === 0) return null;

  return (
    <div className="space-y-3 mb-8">
      {uploads.map((upload, index) => (
        <div
          key={`${upload.file.name}-${index}`}
          className="bg-white border border-gray-200 rounded-lg p-4"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              {/* File Icon */}
              <div className="flex-shrink-0">
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

              {/* File Info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {upload.file.name}
                </p>
                <p className="text-xs text-gray-500">
                  {(upload.file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>

              {/* Status */}
              <div className="flex-shrink-0">
                {upload.status === "uploading" && (
                  <span className="inline-flex items-center gap-2 text-sm text-light-blue">
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
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
                    Uploading...
                  </span>
                )}

                {upload.status === "processing" && (
                  <span className="inline-flex items-center gap-2 text-sm text-lavender">
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
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
                    Processing...
                  </span>
                )}

                {upload.status === "success" && (
                  <span className="inline-flex items-center gap-2 text-sm text-green-600">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                    Ready
                  </span>
                )}

                {upload.status === "error" && (
                  <span className="inline-flex items-center gap-2 text-sm text-red-600">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                        clipRule="evenodd"
                      />
                    </svg>
                    Failed
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Progress Bar (for uploading state) */}
          {upload.status === "uploading" && (
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div
                className="bg-light-blue h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${upload.progress}%` }}
              ></div>
            </div>
          )}

          {/* Processing Message */}
          {upload.status === "processing" && (
            <p className="text-xs text-gray-500 mt-1">
              Analyzing paper and generating embeddings...
            </p>
          )}

          {/* Error Message */}
          {upload.status === "error" && upload.error && (
            <p className="text-xs text-red-600 mt-1">{upload.error}</p>
          )}
        </div>
      ))}
    </div>
  );
}
