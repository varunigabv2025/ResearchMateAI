"use client";

import WorkspaceShell from "@/components/workspace/WorkspaceShell";
import WorkspaceHeader from "@/components/workspace/WorkspaceHeader";

export default function GapsPage() {
  return (
    <WorkspaceShell>
      <WorkspaceHeader
        title="Research Gaps"
        description="AI-suggested research gaps from your papers"
      />

      <div className="bg-white rounded-xl border-2 border-gray-200 p-12 text-center">
        <div className="max-w-md mx-auto">
          <div className="w-16 h-16 bg-muted-rose/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-muted-rose"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
          </div>
          <h3 className="font-serif text-2xl text-gray-900 mb-3">
            Gap Analysis Coming Soon
          </h3>
          <p className="text-gray-600 mb-4">
            The research gap analysis interface will be implemented in the next phase.
          </p>
          <p className="text-xs text-gray-500 italic">
            AI-generated suggestions should be verified against the original literature.
          </p>
        </div>
      </div>
    </WorkspaceShell>
  );
}
