import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../lib/api';

export interface DuplicateGroup {
  id: string;
  size_bytes: number;
  sha256: string;
  member_count: number;
  reclaimable_bytes: number;
  members: Array<{ id: string; file: string; is_keeper: boolean }>;
}

export function DuplicatesView() {
  const { data: groups = [], isLoading } = useQuery<DuplicateGroup[]>({
    queryKey: ['duplicates'],
    queryFn: async () => {
      const { data } = await apiClient.get('/duplicates/');
      return data;
    },
  });

  if (isLoading) {
    return <div className="p-6 animate-pulse">Loading duplicates...</div>;
  }

  return (
    <section className="mx-auto max-w-5xl p-6 space-y-4">
      <h2 className="text-2xl font-semibold tracking-tight">Duplicates</h2>
      {groups.length === 0 && (
        <p className="text-sm text-neutral-500">No duplicate groups detected.</p>
      )}
      <ul className="space-y-2">
        {groups.map((group) => (
          <li key={group.id} className="rounded-md border border-neutral-200 p-4 bg-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-neutral-900">
                  {group.member_count} copies · {(group.size_bytes / 1024).toFixed(1)} KB
                </p>
                <p className="text-xs text-neutral-500">
                  sha256 {group.sha256.slice(0, 16)}…
                </p>
              </div>
              <p className="text-xs text-neutral-500">
                reclaimable {(group.reclaimable_bytes / 1024).toFixed(1)} KB
              </p>
            </div>
            <ul className="mt-2 space-y-1">
              {group.members.map((member) => (
                <li key={member.id} className="text-xs text-neutral-600">
                  {member.file} {member.is_keeper && <span className="text-blue-600">keeper</span>}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </section>
  );
}
