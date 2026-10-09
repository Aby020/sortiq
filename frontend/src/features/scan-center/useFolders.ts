import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../lib/api';

export interface Folder {
  id: string;
  path: string;
  name: string;
  is_active: boolean;
  is_watched: boolean;
  recursive: boolean;
  follow_symlinks: boolean;
  file_count: number;
  total_bytes: number;
  last_scanned_at: string | null;
}

export function useFolders() {
  return useQuery<Folder[]>({
    queryKey: ['folders'],
    queryFn: async () => {
      const { data } = await apiClient.get('/folders/');
      return data;
    },
  });
}

export function useCreateFolder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { path: string; name: string }) => {
      const { data } = await apiClient.post('/folders/', payload);
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['folders'] }),
  });
}

export function useScanFolder(folderId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.post(`/folders/${folderId}/scan/`);
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['folders'] }),
  });
}
