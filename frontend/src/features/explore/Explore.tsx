import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../lib/api';

export interface CatalogItem {
  id: string;
  file_path: string;
  file_name: string;
  size_bytes: number;
  mime_type: string;
  category?: string;
}

export function Explore() {
  const [q, setQ] = useState('');
  const [filter, setFilter] = useState('all');

  const { data: files = [], isLoading } = useQuery<CatalogItem[]>({
    queryKey: ['files', q, filter],
    queryFn: async () => {
      const url = q ? `/files/?search=${encodeURIComponent(q)}` : '/files/';
      const { data } = await apiClient.get(url);
      return (data.results ?? data).filter((f: CatalogItem) => {
        if (filter === 'all') return true;
        return f.mime_type?.includes(filter) || f.category === filter;
      });
    },
  });

  return (
    <section className="mx-auto max-w-6xl p-6 space-y-6">
      <div className="flex items-baseline justify-between gap-4">
        <h1 className="text-4xl font-extrabold tracking-tight">Explore</h1>
        <div className="flex gap-2">
          <input
            type="text"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search files…"
            className="rounded-md border border-neutral-700 bg-neutral-900 px-3 py-1.5 text-sm text-neutral-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
          />
          {['all', 'pdf', 'image', 'text'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                filter === f ? 'bg-blue-600 text-white' : 'bg-neutral-800 text-neutral-300 hover:bg-neutral-700'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="animate-pulse text-sm text-neutral-500">Loading catalog…</div>
      ) : files.length === 0 ? (
        <p className="text-sm text-neutral-500">No files indexed yet.</p>
      ) : (
        <div className="rounded-xl border border-neutral-800 bg-neutral-900/50 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-neutral-800/60 text-xs text-neutral-400 uppercase tracking-wider">
              <tr>
                <th className="text-left px-4 py-2">File</th>
                <th className="text-left px-4 py-2">Size</th>
                <th className="text-left px-4 py-2">Type</th>
              </tr>
            </thead>
            <tbody>
              {files.map((f) => (
                <tr key={f.id} className="border-t border-neutral-800 hover:bg-neutral-800/30">
                  <td className="px-4 py-2 text-neutral-200">{f.file_name}</td>
                  <td className="px-4 py-2 text-neutral-400">{(f.size_bytes / 1024).toFixed(1)} KB</td>
                  <td className="px-4 py-2 text-neutral-500">{f.mime_type || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
