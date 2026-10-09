import { motion } from 'framer-motion';


export function Dashboard() {
  const storage = 0.42;
  return (
    <section className="mx-auto max-w-6xl p-6 space-y-6">
      <div className="flex items-baseline justify-between gap-4">
        <h1 className="text-4xl font-extrabold tracking-tight">Dashboard</h1>
        <span className="text-xs font-medium text-blue-600">Live</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 rounded-xl bg-neutral-900 border border-neutral-800">
          <p className="text-xs text-neutral-400 uppercase tracking-wider">Storage used</p>
          <p className="text-3xl font-bold text-white mt-1">{Math.round(storage * 100)}%</p>
          <div className="h-2 w-full bg-neutral-800 rounded-full mt-3 overflow-hidden"><div className="h-full w-[42%] bg-blue-500 rounded-full" /></div>
        </div>
        <div className="p-5 rounded-xl bg-neutral-900 border border-neutral-800">
          <p className="text-xs text-neutral-400 uppercase tracking-wider">Pending actions</p>
          <p className="text-3xl font-bold text-white mt-1">3</p>
          <p className="text-sm text-neutral-300 mt-1">Moves queued by rules engine</p>
        </div>
        <div className="p-5 rounded-xl bg-neutral-900 border border-neutral-800">
          <p className="text-xs text-neutral-400 uppercase tracking-wider">Scans today</p>
          <p className="text-3xl font-bold text-white mt-1">12</p>
          <p className="text-sm text-neutral-300 mt-1">Folders indexed incrementally</p>
        </div>
      </div>
      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="rounded-xl border border-neutral-800 bg-neutral-900/50 p-6">
        <h2 className="text-xl font-semibold tracking-tight">Recent activity</h2>
        <table className="w-full text-sm mt-4">
          <thead><tr className="text-left text-neutral-400"><th className="py-2">Event</th><th className="py-2">Target</th><th className="py-2">Status</th></tr></thead>
          <tbody>
            {[
              { e: "Scan completed", t: "/home/docs", s: "success" },
              { e: "Rule dry-run", t: "/downloads", s: "pending" },
              { e: "Duplicate group", t: "3 items", s: "review" },
            ].map((r) => (
              <tr key={r.e} className="border-t border-neutral-800"><td className="py-2 text-neutral-200">{r.e}</td><td className="py-2 text-neutral-400">{r.t}</td><td className="py-2"><span className={`text-xs px-2 py-0.5 rounded-full ${r.s === "success" ? "bg-emerald-900 text-emerald-300" : r.s === "pending" ? "bg-amber-900 text-amber-300" : "bg-blue-900 text-blue-300"}`}>{r.s}</span></td></tr>
            ))}
          </tbody>
        </table>
      </motion.div>
    </section>
  );
}
