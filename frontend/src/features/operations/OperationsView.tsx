import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../../lib/api';

export interface Operation {
  id: string;
  status: string;
  total_items: number;
  successful_items: number;
  failed_items: number;
  started_at: string | null;
  completed_at: string | null;
}

export function useOperations() {
  return useQuery<Operation[]>({
    queryKey: ['operations'],
    queryFn: async () => {
      const { data } = await apiClient.get('/operations/');
      return data;
    },
  });
}

export function useRollbackOperation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (operationId: string) => {
      const { data } = await apiClient.post(
        `/operations/${operationId}/rollback/`
      );
      return data;
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['operations'] }),
  });
}

export function OperationsView() {
  const { data: operations = [], isLoading } = useOperations();
  const rollback = useRollbackOperation();

  if (isLoading) {
    return <div className="p-6 animate-pulse">Loading operations...</div>;
  }

  return (
    <section className="mx-auto max-w-5xl p-6 space-y-4">
      <h2 className="text-2xl font-semibold tracking-tight">Operations</h2>
      {operations.length === 0 && (
        <p className="text-sm text-neutral-500">No operations recorded.</p>
      )}
      <ul className="space-y-2">
        {operations.map((op) => (
          <li key={op.id} className="rounded-md border border-neutral-200 p-4 bg-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-neutral-900">
                  {op.status}
                </p>
                <p className="text-xs text-neutral-500">
                  {op.successful_items}/{op.total_items} items
                </p>
              </div>
              <button
                type="button"
                onClick={() => rollback.mutate(op.id)}
                disabled={rollback.isPending}
                className="rounded-md border border-neutral-300 px-3 py-1.5 text-xs font-medium text-neutral-700 hover:bg-neutral-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
              >
                {rollback.isPending ? 'Rolling back…' : 'Rollback'}
              </button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
