/**
 * API client functions for Q&A operations
 */

import { config } from '../config';
import type { QuestionResponse } from '../types/paper';

const API_BASE = config.apiUrl;

export interface AskQuestionRequest {
  question: string;
}

/**
 * Ask a question about a specific paper
 * 
 * @param paperId - UUID of the paper to query
 * @param question - The question to ask about the paper
 * @returns Grounded answer with source citations
 * @throws Error if the request fails
 */
export async function askQuestion(
  paperId: string,
  question: string
): Promise<QuestionResponse> {
  const response = await fetch(`${API_BASE}/api/papers/${paperId}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Failed to get answer: ${response.statusText}`
    );
  }

  return response.json();
}
