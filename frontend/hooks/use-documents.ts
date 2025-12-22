/**
 * TanStack Query hooks for document operations.
 * Use these for ALL server state management.
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import type { Document, DocumentCreate, DocumentUpdate } from '@/types/api';

// Query keys
export const documentKeys = {
  all: ['documents'] as const,
  lists: () => [...documentKeys.all, 'list'] as const,
  list: (filters: { skip?: number; limit?: number }) =>
    [...documentKeys.lists(), filters] as const,
  details: () => [...documentKeys.all, 'detail'] as const,
  detail: (id: string) => [...documentKeys.details(), id] as const,
};

// Hooks
export function useDocuments(skip?: number, limit?: number) {
  return useQuery({
    queryKey: documentKeys.list({ skip, limit }),
    queryFn: () => apiClient.documents.getAll(skip, limit),
  });
}

export function useDocument(id: string) {
  return useQuery({
    queryKey: documentKeys.detail(id),
    queryFn: () => apiClient.documents.getById(id),
    enabled: !!id,
  });
}

export function useCreateDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: DocumentCreate) => apiClient.documents.create(data),
    onSuccess: () => {
      // Invalidate and refetch documents list
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

export function useUpdateDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DocumentUpdate }) =>
      apiClient.documents.update(id, data),
    onSuccess: (_, variables) => {
      // Invalidate specific document and list
      queryClient.invalidateQueries({ queryKey: documentKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.documents.delete(id),
    onSuccess: () => {
      // Invalidate documents list
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}
