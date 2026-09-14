/**
 * API client functions for paper management
 */

import { config } from '../config';
import type { Paper, PaperListResponse, PaperUploadResponse } from '../types/paper';

const API_BASE = config.apiUrl;

/**
 * Fetch all papers
 */
export async function listPapers(): Promise<Paper[]> {
  const response = await fetch(`${API_BASE}/api/papers/`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch papers: ${response.statusText}`);
  }

  const data: PaperListResponse = await response.json();
  return data.papers;
}

/**
 * Upload a single PDF paper
 */
export async function uploadPaper(file: File): Promise<PaperUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/api/papers/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Delete a paper by ID
 */
export async function deletePaper(paperId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/papers/${paperId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Delete failed: ${response.statusText}`);
  }
}

/**
 * Get a single paper by ID
 */
export async function getPaper(paperId: string): Promise<Paper> {
  const response = await fetch(`${API_BASE}/api/papers/${paperId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch paper: ${response.statusText}`);
  }

  return response.json();
}
