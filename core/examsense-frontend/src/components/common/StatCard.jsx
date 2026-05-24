// afisam un card simplu pentru o statistica din dashboard sau admin
export default function StatCard({ label, value, hint }) {
  return (
    <div className="rounded-3xl border border-slate-200/70 bg-white/90 p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">{value}</p>
      {hint && <p className="mt-2 text-sm text-slate-400">{hint}</p>}
    </div>
  )
}