"use client";

import { useCallback, useState } from "react";
import { config } from "@/lib/config";

interface UploadZoneProps {
  onFilesSelected: (files: File[]) => void;
  disabled?: boolean;
}

export default function UploadZone({ onFilesSelected, disabled = false }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragging(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      if (disabled) return;

      const files = Array.from(e.dataTransfer.files).filter(
        (file) => file.type === "application/pdf"
      );

      if (files.length > 0) {
        onFilesSelected(files);
      }
    },
    [disabled, onFilesSelected]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (disabled) return;

      const files = e.target.files ? Array.from(e.target.files) : [];
      if (files.length > 0) {
        onFilesSelected(files);
      }
      // Reset input value to allow selecting the same file again
      e.target.value = "";
    },
    [disabled, onFilesSelected]
  );

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
        isDragging
          ? "border-light-blue bg-light-blue/5 scale-[1.02]"
          : "border-gray-300 bg-white hover:border-light-blue/50"
      } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
    >
      <input
        type="file"
        id="file-upload"
        className="sr-only"
        accept={config.acceptedFileTypes}
        multiple
        onChange={handleFileInput}
        disabled={disabled}
      />

      <label
        htmlFor="file-upload"
        className={`cursor-pointer ${disabled ? "cursor-not-allowed" : ""}`}
      >
        <div className="flex flex-col items-center gap-4">
          {/* Upload Icon */}
          <div className="w-16 h-16 rounded-full bg-light-blue/10 flex items-center justify-center">
            <svg
              className="w-8 h-8 text-light-blue"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>

          {/* Text */}
          <div>
            <h3 className="font-serif text-2xl text-gray-900 mb-2">
              Add research papers
            </h3>
            <p className="text-gray-600 mb-4">
              Drop PDF files here or browse your files
            </p>
            <p className="text-sm text-gray-500">
              PDF • Up to {config.maxPapersForComparison} papers
            </p>
          </div>

          {/* Browse Button */}
          <button
            type="button"
            className="px-6 py-3 bg-light-blue text-white rounded-lg hover:bg-light-blue/90 transition-all hover:shadow-md font-medium"
            disabled={disabled}
          >
            Browse Files
          </button>
        </div>
      </label>
    </div>
  );
}
