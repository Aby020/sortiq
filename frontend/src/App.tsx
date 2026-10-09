import { useState } from 'react';
import { Dashboard } from './features/dashboard/Dashboard';
import { ScanCenter } from './features/scan-center/ScanCenter';
import { DuplicatesView } from './features/duplicates/DuplicatesView';
import { OperationsView } from './features/operations/OperationsView';
import { SettingsPage } from './features/settings/SettingsPage';
import { Explore } from './features/explore/Explore';

export default function App() {
  const [tab, setTab] = useState('dashboard');

  const tabs = [
    { key: 'dashboard', label: 'Dashboard' },
    { key: 'scan', label: 'Scan' },
    { key: 'duplicates', label: 'Duplicates' },
    { key: 'operations', label: 'Operations' },
    { key: 'explore', label: 'Explore' },
    { key: 'settings', label: 'Settings' },
  ];

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 font-sans selection:bg-blue-500/30">
      {/* Top navigation */}
      <nav className="sticky top-0 z-50 border-b border-neutral-800 bg-neutral-950/80 backdrop-blur-md">
        <div className="mx-auto max-w-6xl px-6 py-3 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-xl font-extrabold tracking-tight text-white">Sortiq</span>
            <span className="text-xs font-medium text-neutral-500">v1.0.0</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-950 px-2.5 py-0.5 text-xs font-medium text-emerald-300 border border-emerald-800">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              :8000 OK
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-950 px-2.5 py-0.5 text-xs font-medium text-blue-300 border border-blue-800">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-400 animate-pulse" />
              :8100 OK
            </span>
            <a
              href="http://localhost:8000/admin/"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-md bg-neutral-800 px-3 py-1 text-xs font-medium text-neutral-200 hover:bg-neutral-700 transition-colors border border-neutral-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500"
            >
              Admin
            </a>
          </div>
        </div>
        <div className="mx-auto max-w-6xl px-6 flex gap-1 overflow-x-auto">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`rounded-t-md px-4 py-2 text-sm font-medium transition-colors border-b-2 ${
                tab === t.key
                  ? 'text-blue-400 border-blue-400 bg-neutral-900/60'
                  : 'text-neutral-400 border-transparent hover:text-neutral-200 hover:bg-neutral-900/30'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="mx-auto max-w-6xl px-6 py-8">
        {tab === 'dashboard' && <Dashboard />}
        {tab === 'scan' && <ScanCenter />}
        {tab === 'duplicates' && <DuplicatesView />}
        {tab === 'operations' && <OperationsView />}
        {tab === 'explore' && <Explore />}
        {tab === 'settings' && <SettingsPage />}
      </main>

      <footer className="mx-auto max-w-6xl px-6 py-8 text-xs text-neutral-600 border-t border-neutral-900">
        Sortiq Intelligent Desktop File Management — Control plane :8000 · Execution :8100 · No AI attribution.
      </footer>
    </div>
  );
}
