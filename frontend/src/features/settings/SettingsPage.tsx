import { motion } from 'framer-motion';
export function SettingsPage() {
  return (
    <section className="mx-auto max-w-3xl p-6 space-y-6">
      <h1 className="text-4xl font-extrabold tracking-tight">Settings</h1>
      <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="rounded-xl border border-neutral-800 bg-neutral-900/50 p-6 space-y-4">
        <div>
          <label htmlFor="conflict" className="text-xs font-semibold text-neutral-300 uppercase tracking-wider">Conflict policy</label>
          <select id="conflict" className="mt-2 w-full rounded-md bg-neutral-800 border border-neutral-700 px-3 py-2 text-sm text-neutral-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"><option>skip</option><option>autorename</option></select>
        </div>
        <div>
          <label htmlFor="interval" className="text-xs font-semibold text-neutral-300 uppercase tracking-wider">Auto-scan interval</label>
          <select id="interval" className="mt-2 w-full rounded-md bg-neutral-800 border border-neutral-700 px-3 py-2 text-sm text-neutral-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"><option>15 min</option><option>1 hr</option></select>
        </div>
      </motion.div>
    </section>
  );
}
