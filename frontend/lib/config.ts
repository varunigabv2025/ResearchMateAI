/**
 * Application configuration
 */

export const config = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  maxPapersForComparison: 5,
  minPapersForComparison: 2,
  acceptedFileTypes: '.pdf',
  maxFileSize: 20 * 1024 * 1024, // 20MB in bytes
} as const;
