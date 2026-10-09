import { useState } from 'react';
import { useFolders, useCreateFolder, useScanFolder } from './useFolders';

export function ScanCenter() {
  const { data: folders = [], isLoading } = useFolders();
  const createFolder = useCreateFolder();
  const [newPath, setNewPath] = useState('');

  const handleAdd = () => {
    if (!newPath.trim()) return;
    createFolder.mutate({ path: newPath, name: newPath.split('/').pop() || newPath });
    setNewPath('');
  };

  if (isLoading) {
    return <div className="p-6 animate-pulse">Loading folders...</div>;
  }

  return (
    <section className="mx-auto max-w-5xl p-6 space-y-6">
      <h2 className="text-2xl font-semibold tracking-tight">Scan Center</h2>
      <div className="flex gap-2">
        <input
          type="text"
          value={newPath}
          onChange={(e) => setNewPath(e.target.value)}
          placeholder="Folder path to manage"
          className="flex-1 rounded-md border border-neutral-300 px-3 py-2 text-sm"
          aria-label="Folder path"
        />
        <button
          type="button"
          onClick={handleAdd}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
        >
          Add folder
        </button>
      </div>
      <ul className="space-y-2">
        {folders.length === 0 && <li className="text-sm text-neutral-500">No folders registered.</li>}
        {folders.map((folder) => (
          <li key={folder.id} className="rounded-md border border-neutral-200 p-4 bg-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-neutral-900">{folder.name}</p>
                <p className="text-xs text-neutral-500">{folder.path}</p>
              </div>
              <ScanButton folderId={folder.id} />
            </div>
            <p className="mt-2 text-xs text-neutral-500">
              {folder.file_count} files · {(folder.total_bytes / 1024 / 1024).toFixed(1)} MB
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}

function ScanButton({ folderId }: { folderId: string }) {
  const scan = useScanFolder(folderId);
  return (
    <button
      type="button"
      onClick={() => scan.mutate()}
      disabled={scan.isPending}
      className="rounded-md border border-neutral-300 px-3 py-1.5 text-xs font-medium text-neutral-700 hover:bg-neutral-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
    >
      {scan.isPending ? 'Scanning…' : 'Scan'}
    </button>
  );
}
