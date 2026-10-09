import { motion } from 'framer-motion';
export function Explore() {
  return (
    <section className="mx-auto max-w-6xl p-6">
      <h1 className="text-4xl font-extrabold tracking-tight mb-6">Explore</h1>
      <div className="flex gap-2 mb-4">
        <button className="px-3 py-1.5 rounded-md bg-neutral-800 text-xs font-medium">All</button>
        <button className="px-3 py-1.5 rounded-md bg-neutral-900 text-xs font-medium text-neutral-400">Documents</button>
        <button className="px-3 py-1.5 rounded-md bg-neutral-900 text-xs font-medium text-neutral-400">Images</button>
        <button className="px-3 py-1.5 rounded-md bg-neutral-900 text-xs font-medium text-neutral-400">Archives</button>
      </div>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="rounded-xl border border-neutral-800 bg-neutral-900/50 p-4 space-y-2">
        <div className="flex items-center justify-between py-2 border-b border-neutral-800"><span className="text-sm font-medium text-neutral-200">report.pdf</span><span className="text-xs text-neutral-500">4.2 MB</span></div>
        <div className="flex items-center justify-between py-2 border-b border-neutral-800"><span className="text-sm font-medium text-neutral-200">notes.md</span><span className="text-xs text-neutral-500">12 KB</span></div>
        <div className="flex items-center justify-between py-2"><span className="text-sm font-medium text-neutral-200">backup.iso</span><span className="text-xs text-neutral-500">2.4 GB</span></div>
      </motion.div>
    </section>
  );
}
