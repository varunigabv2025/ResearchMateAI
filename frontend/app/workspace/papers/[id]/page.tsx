"use client";

import { useParams } from "next/navigation";
import WorkspaceShell from "@/components/workspace/WorkspaceShell";
import WorkspaceHeader from "@/components/workspace/WorkspaceHeader";

export default function PaperDetailPage() {
  const params = useParams();
  const paperId = params.id as string;

  return (
    <WorkspaceShell>
      <WorkspaceHeader
        title="Paper Q&A"
        description="Ask questions about this paper"
      />

      <div className="bg-white rounded-xl border-2 border-gray-200 p-12 text-center">
        <div className="max-w-md mx-auto">
          <div className="w-16 h-16 bg-lavender/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-8 h-8 text-lavender"
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
          <h3 className="font-serif text-2xl text-gray-900 mb-3">
            Q&A Interface Coming Soon
          </h3>
          <p className="text-gray-600 mb-4">
            The paper Q&A interface will be implemented in the next phase.
          </p>
          <p className="text-sm text-gray-500">
            Paper ID: <code className="bg-gray-100 px-2 py-1 rounded">{paperId}</code>
          </p>
        </div>
      </div>
    </WorkspaceShell>
  );
}
