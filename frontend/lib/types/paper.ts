/**
 * TypeScript types matching backend API responses
 */

export interface Paper {
  id: string;
  filename: string;
  original_filename: string;
  file_size_bytes: number;
  page_count: number;
  upload_timestamp: string;
  processed: boolean;
  processing_error: string | null;
  paper_metadata: Record<string, any> | null;
}

export interface PaperDetail extends Paper {
  sections_detected: string[] | null;
}

export interface PaperUploadResponse {
  id: string;
  filename: string;
  page_count: number;
  sections_detected: string[];
  message: string;
}

export interface PaperListResponse {
  papers: Paper[];
  total: number;
}

export interface SourceCitation {
  chunk_id: string;
  page_number: number;
  section: string | null;
  similarity: number;
}

export interface QuestionResponse {
  answer: string;
  sources: SourceCitation[];
  paper_id: string;
  question: string;
  has_sufficient_context: boolean;
}

export interface UploadProgress {
  file: File;
  status: 'idle' | 'uploading' | 'processing' | 'success' | 'error';
  progress: number;
  error?: string;
  paperId?: string;
}
