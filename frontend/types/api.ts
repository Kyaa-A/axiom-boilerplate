/**
 * Type definitions for API requests and responses.
 * Keep these in sync with backend schemas.
 */

export interface Document {
  id: string;
  title: string;
  content: string;
  source?: string;
  vector_id?: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentCreate {
  title: string;
  content: string;
  source?: string;
}

export interface DocumentUpdate {
  title?: string;
  content?: string;
  source?: string;
}

export interface QueryRequest {
  query: string;
  top_k?: number;
  score_threshold?: number;
}

export interface QueryResponse {
  query: string;
  response: string;
  sources: Array<{
    id: string;
    score: number;
    metadata: Record<string, any>;
  }>;
}

export interface GenerateRequest {
  prompt: string;
  system_prompt?: string;
  max_tokens?: number;
}

export interface GenerateResponse {
  response: string;
}

export interface APIError {
  detail: string;
}
