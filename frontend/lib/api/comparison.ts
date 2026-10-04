/**
 * API client for paper comparison and gap analysis
 */

import { config } from '../config';
import type {
  ComparePapersRequest,
  ComparePapersResponse,
  AnalyzeGapsRequest,
  AnalyzeGapsResponse,
} from '../types/comparison';

const API_BASE = config.apiUrl;

/**
 * Compare 2-5 research papers
 */
export async function comparePapers(
  paperIds: string[]
): Promise<ComparePapersResponse> {
  const response = await fetch(`${API_BASE}/api/papers/compare`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ paper_ids: paperIds } as ComparePapersRequest),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Comparison failed: ${response.statusText}`
    );
  }

  return response.json();
}

/**
 * Analyze research gaps from 2-5 papers
 */
export async function analyzeGaps(
  paperIds: string[]
): Promise<AnalyzeGapsResponse> {
  const response = await fetch(`${API_BASE}/api/papers/gaps`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ paper_ids: paperIds } as AnalyzeGapsRequest),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Gap analysis failed: ${response.statusText}`
    );
  }

  return response.json();
}
