/**
 * TanStack Query hooks for AI operations.
 * IMPORTANT: These are the ONLY way frontend should access AI capabilities.
 */
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { QueryRequest, QueryResponse, GenerateRequest, GenerateResponse } from '@/types/api';

/**
 * Hook for RAG queries.
 * Searches documents and generates responses based on context.
 */
export function useRAGQuery() {
  return useMutation({
    mutationFn: (data: QueryRequest) => apiClient.ai.query(data),
    onError: (error) => {
      console.error('RAG query failed:', error);
    },
  });
}

/**
 * Hook for direct LLM generation.
 * Use for tasks that don't require document retrieval.
 */
export function useGenerate() {
  return useMutation({
    mutationFn: (data: GenerateRequest) => apiClient.ai.generate(data),
    onError: (error) => {
      console.error('Generation failed:', error);
    },
  });
}

/**
 * Example usage in a component:
 *
 * function QueryComponent() {
 *   const { mutate: query, data, isLoading } = useRAGQuery();
 *
 *   const handleSubmit = (queryText: string) => {
 *     query({
 *       query: queryText,
 *       top_k: 5,
 *       score_threshold: 0.7,
 *     });
 *   };
 *
 *   return (
 *     <div>
 *       {isLoading && <p>Loading...</p>}
 *       {data && <p>{data.response}</p>}
 *     </div>
 *   );
 * }
 */
