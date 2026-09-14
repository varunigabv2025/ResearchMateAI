"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import WorkspaceShell from "@/components/workspace/WorkspaceShell";
import WorkspaceHeader from "@/components/workspace/WorkspaceHeader";
import UploadZone from "@/components/workspace/UploadZone";
import UploadQueue from "@/components/workspace/UploadQueue";
import PaperGrid from "@/components/workspace/PaperGrid";
import PaperSelectionBar from "@/components/workspace/PaperSelectionBar";
import DeletePaperDialog from "@/components/workspace/DeletePaperDialog";
import { listPapers, uploadPaper, deletePaper } from "@/lib/api/papers";
import type { Paper, UploadProgress } from "@/lib/types/paper";
import { config } from "@/lib/config";

export default function WorkspacePage() {
  const router = useRouter();
  const [papers, setPapers] = useState<Paper[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [uploads, setUploads] = useState<UploadProgress[]>([]);
  const [selectedPaperIds, setSelectedPaperIds] = useState<string[]>([]);
  const [deleteDialog, setDeleteDialog] = useState<{
    isOpen: boolean;
    paperId?: string;
    paperName?: string;
  }>({ isOpen: false });
  const [isDeleting, setIsDeleting] = useState(false);

  // Load papers on mount
  const loadPapers = useCallback(async () => {
    try {
      setIsLoading(true);
      const fetchedPapers = await listPapers();
      setPapers(fetchedPapers);
    } catch (error) {
      console.error("Failed to load papers:", error);
      // TODO: Show error toast
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPapers();
  }, [loadPapers]);

  // Handle file selection
  const handleFilesSelected = useCallback(
    async (files: File[]) => {
      // Validate file size
      const validFiles = files.filter((file) => {
        if (file.size > config.maxFileSize) {
          console.error(`File ${file.name} exceeds maximum size`);
          return false;
        }
        return true;
      });

      if (validFiles.length === 0) return;

      // Create upload progress entries
      const newUploads: UploadProgress[] = validFiles.map((file) => ({
        file,
        status: "idle",
        progress: 0,
      }));

      setUploads((prev) => [...prev, ...newUploads]);

      // Upload files sequentially
      for (let i = 0; i < validFiles.length; i++) {
        const file = validFiles[i];
        const uploadIndex = uploads.length + i;

        try {
          // Update to uploading
          setUploads((prev) =>
            prev.map((upload, idx) =>
              idx === uploadIndex
                ? { ...upload, status: "uploading", progress: 50 }
                : upload
            )
          );

          // Upload file
          const response = await uploadPaper(file);

          // Update to processing
          setUploads((prev) =>
            prev.map((upload, idx) =>
              idx === uploadIndex
                ? {
                    ...upload,
                    status: "processing",
                    progress: 100,
                    paperId: response.id,
                  }
                : upload
            )
          );

          // Wait a bit then mark as success
          setTimeout(() => {
            setUploads((prev) =>
              prev.map((upload, idx) =>
                idx === uploadIndex ? { ...upload, status: "success" } : upload
              )
            );

            // Reload papers
            loadPapers();

            // Remove from upload queue after a delay
            setTimeout(() => {
              setUploads((prev) => prev.filter((_, idx) => idx !== uploadIndex));
            }, 2000);
          }, 1000);
        } catch (error) {
          console.error("Upload failed:", error);
          setUploads((prev) =>
            prev.map((upload, idx) =>
              idx === uploadIndex
                ? {
                    ...upload,
                    status: "error",
                    error:
                      error instanceof Error
                        ? error.message
                        : "Upload failed. Please try again.",
                  }
                : upload
            )
          );
        }
      }
    },
    [uploads.length, loadPapers]
  );

  // Handle paper selection
  const handleSelectPaper = useCallback((paperId: string) => {
    setSelectedPaperIds((prev) => {
      if (prev.includes(paperId)) {
        return prev.filter((id) => id !== paperId);
      } else {
        // Enforce max selection limit
        if (prev.length >= config.maxPapersForComparison) {
          return prev;
        }
        return [...prev, paperId];
      }
    });
  }, []);

  // Handle compare action
  const handleCompare = useCallback(() => {
    // Navigate to compare page with selected paper IDs
    const params = new URLSearchParams();
    selectedPaperIds.forEach((id) => params.append("papers", id));
    router.push(`/workspace/compare?${params.toString()}`);
  }, [selectedPaperIds, router]);

  // Handle delete paper
  const handleDeleteClick = useCallback((paperId: string) => {
    const paper = papers.find((p) => p.id === paperId);
    setDeleteDialog({
      isOpen: true,
      paperId,
      paperName: paper?.original_filename || paper?.filename,
    });
  }, [papers]);

  const handleDeleteConfirm = useCallback(async () => {
    if (!deleteDialog.paperId) return;

    try {
      setIsDeleting(true);
      await deletePaper(deleteDialog.paperId);
      
      // Remove from selected if it was selected
      setSelectedPaperIds((prev) =>
        prev.filter((id) => id !== deleteDialog.paperId)
      );

      // Reload papers
      await loadPapers();

      // Close dialog
      setDeleteDialog({ isOpen: false });
    } catch (error) {
      console.error("Failed to delete paper:", error);
      // TODO: Show error toast
    } finally {
      setIsDeleting(false);
    }
  }, [deleteDialog.paperId, loadPapers]);

  const handleDeleteCancel = useCallback(() => {
    if (!isDeleting) {
      setDeleteDialog({ isOpen: false });
    }
  }, [isDeleting]);

  // Handle ask question
  const handleAskQuestion = useCallback(
    (paperId: string) => {
      router.push(`/workspace/papers/${paperId}`);
    },
    [router]
  );

  // Recent papers for sidebar (last 3)
  const recentPapers = papers
    .slice()
    .sort(
      (a, b) =>
        new Date(b.upload_timestamp).getTime() -
        new Date(a.upload_timestamp).getTime()
    )
    .slice(0, 3)
    .map((p) => ({
      id: p.id,
      filename: p.original_filename || p.filename,
    }));

  return (
    <WorkspaceShell recentPapers={recentPapers}>
      <WorkspaceHeader
        title="Your Research Workspace"
        description="Your papers, ready to analyze."
      />

      {/* Upload Zone */}
      <div className="mb-8">
        <UploadZone
          onFilesSelected={handleFilesSelected}
          disabled={uploads.some((u) => u.status === "uploading")}
        />
      </div>

      {/* Upload Queue */}
      <UploadQueue uploads={uploads} />

      {/* Paper Grid */}
      <PaperGrid
        papers={papers}
        selectedPaperIds={selectedPaperIds}
        onSelectPaper={handleSelectPaper}
        onDeletePaper={handleDeleteClick}
        onAskQuestion={handleAskQuestion}
        isLoading={isLoading}
      />

      {/* Selection Bar */}
      <PaperSelectionBar
        selectedCount={selectedPaperIds.length}
        onCompare={handleCompare}
        onClear={() => setSelectedPaperIds([])}
      />

      {/* Delete Dialog */}
      <DeletePaperDialog
        isOpen={deleteDialog.isOpen}
        paperName={deleteDialog.paperName}
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
        isDeleting={isDeleting}
      />
    </WorkspaceShell>
  );
}
