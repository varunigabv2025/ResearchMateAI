"use client";

import Sidebar from "./Sidebar";

interface WorkspaceShellProps {
  children: React.ReactNode;
  recentPapers?: Array<{ id: string; filename: string }>;
}

export default function WorkspaceShell({
  children,
  recentPapers,
}: WorkspaceShellProps) {
  return (
    <div className="flex min-h-screen bg-cream">
      {/* Sidebar */}
      <Sidebar recentPapers={recentPapers} />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>
    </div>
  );
}
