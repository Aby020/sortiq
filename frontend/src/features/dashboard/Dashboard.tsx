import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { apiClient } from '../../lib/api';
import { useOperations } from '../operations/OperationsView';
import { useFolders } from '../scan-center/useFolders';

export interface DashboardStats {
  files: number;
  duplicateGroups: number;
  activeOperations: number;
  registeredFolders: number;
}

function useDashboardStats(): DashboardStats {
  const { data: files = [] } = useQuery({
    queryKey: ['files'],
    queryFn: async () => {
      const { data } = await apiClient.get('/files/');
      return data.results ?? data;
    },
  });
  const { data: groups = [] } = useQuery({
    queryKey: ['duplicates'],
    queryFn: async () => {
      const { data } = await apiClient.get('/duplicates/');
      return data.results ?? data;
    },
  });
  const { data: folders = [] } = useFolders();
  const { data: operations = [] } = useOperations();

  const activeOperations = operations.filter((op) => op.status === 'running').length;

  return {
    files: files.length,
    duplicateGroups: groups.length,
    activeOperations,
    registeredFolders: folders.length,
  };
}

function Stat({ label, value, hint }: { label: string; value: string | number; hint: string }) {
  return (
    <div className="p-5 rounded-xl bg-neutral-900 border border-neutral-800">
      <p className="text-xs text-neutral-400 uppercase tracking-wider">{label}</p>
      <p className="text-3xl font-bold text-white mt-1">{value}</p>
      <p className="text-sm text-neutral-400 mt-1">{hint}</p>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="rounded-xl border border-dashed border-neutral-800 bg-neutral-900/40 p-12 text-center">
      <p className="text-lg font-semibold text-neutral-200">No directories scanned yet</p>
      <p className="text-sm text-neutral-500 mt-1">
        Register a folder in the Scan tab to begin cataloging files.
      </p>
    </div>
  );
}

export function Dashboard() {
  const stats = useDashboardStats();
  const { data: activity = [], isLoading } = useQuery({
    queryKey: ['activity'],
    queryFn: async () => {
      const { data } = await apiClient.get('/activity/');
      return data.results ?? data;
    },
  });


  return (
    <section className="space-y-6">
      <div className="flex items-baseline justify-between gap-4">
        <h1 className="text-4xl font-extrabold tracking-tight">Dashboard</h1>
        {stats.activeOperations > 0 && (
          <span className="text-xs font-medium text-blue-400">{stats.activeOperations} jobs running</span>
        )}
      </div>

      {stats.registeredFolders === 0 ? (
        <EmptyState />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Stat label="Files cataloged" value={stats.files} hint="indexed across folders" />
            <Stat label="Duplicate groups" value={stats.duplicateGroups} hint="awaiting review" />
            <Stat label="Active jobs" value={stats.activeOperations} hint="operations in progress" />
            <Stat label="Registered folders" value={stats.registeredFolders} hint="sources being watched" />
          </div>

          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-xl border border-neutral-800 bg-neutral-900/50 p-6"
          >
            <div className="flex items-baseline justify-between">
              <h2 className="text-xl font-semibold tracking-tight">Recent activity</h2>
              {isLoading && <span className="text-xs text-neutral-500">Loading…</span>}
            </div>
            {activity.length === 0 ? (
              <p className="text-sm text-neutral-500 mt-4">No activity recorded yet.</p>
            ) : (
              <table className="w-full text-sm mt-4">
                <thead>
                  <tr className="text-left text-neutral-400">
                    <th className="py-2">Event</th>
                    <th className="py-2">Target</th>
                    <th className="py-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {activity.slice(0, 8).map((entry: { id: string; event: string; target: string; status: string }) => (
                    <tr key={entry.id} className="border-t border-neutral-800">
                      <td className="py-2 text-neutral-200">{entry.event}</td>
                      <td className="py-2 text-neutral-400">{entry.target}</td>
                      <td className="py-2">
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${
                            entry.status === 'success'
                              ? 'bg-emerald-900 text-emerald-300'
                              : entry.status === 'pending'
                                ? 'bg-amber-900 text-amber-300'
                                : 'bg-blue-900 text-blue-300'
                          }`}
                        >
                          {entry.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </motion.div>
        </>
      )}
    </section>
  );
}
