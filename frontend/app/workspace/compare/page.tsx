"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import WorkspaceShell from "@/components/workspace/WorkspaceShell";
import WorkspaceHeader from "@/components/workspace/WorkspaceHeader";

function CompareContent() {
  const searchParams = useSearchParams();
  const paperIds = searchParams.getAll("papers");

  return (
    <div className="bg-white rounded-xl border-2 border-gray-200 p-12 text-center">
      <div className="max-w-md mx-auto">
        <div className="w-16 h-16 bg-light-blue/10 rounded-full flex items-center justify-center mx-auto mb-4">
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
              d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"
            />
          </svg>
        </div>
        <h3 className="font-serif text-2xl text-gray-900 mb-3">
          Comparison Interface Coming Soon
        </h3>
        <p className="text-gray-600 mb-4">
          The paper comparison interface will be implemented in the next phase.
        </p>
        {paperIds.length > 0 && (
          <div className="text-sm text-gray-500">
            <p className="mb-2">Selected {paperIds.length} papers for comparison:</p>
            <div className="space-y-1">
              {paperIds.map((id, index) => (
                <div key={id} className="bg-gray-100 px-3 py-2 rounded">
                  Paper {index + 1}: <code className="text-xs">{id}</code>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ComparePage() {
  return (
    <WorkspaceShell>
      <WorkspaceHeader
        title="Compare Papers"
        description="Side-by-side comparison of research papers"
      />

      <Suspense fallback={
        <div className="bg-white rounded-xl border-2 border-gray-200 p-12 text-center">
          <div className="flex items-center justify-center">
            <svg className="animate-spin h-8 w-8 text-light-blue" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        </div>
      }>
        <CompareContent />
      </Suspense>
    </WorkspaceShell>
  );
}
