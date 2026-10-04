/**
 * TypeScript types for paper comparison and gap analysis
 * Based on backend Pydantic schemas
 */

export interface ComparePapersRequest {
  paper_ids: string[]; // 2-5 paper IDs
}

export interface PaperComparisonResult {
  paper_id: string;
  filename: string;
  method: string;
  dataset: string;
  metric_result: string;
  limitation: string;
}

export interface ComparePapersResponse {
  papers: PaperComparisonResult[];
  total_papers: number;
}

export interface AnalyzeGapsRequest {
  paper_ids: string[]; // 2-5 paper IDs
}

export interface ResearchGap {
  title: string;
  description: string;
  basis: string;
}

export interface AnalyzeGapsResponse {
  paper_ids: string[];
  gaps: ResearchGap[];
  disclaimer: string;
}
