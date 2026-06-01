export default function StatCard({
  label,
  value,
  hint,
  accent = 'default',
}) {
  const accentClasses = {
    default: 'border-slate-200/80 from-white to-slate-50',
    brand: 'border-brand-200/70 from-brand-50 to-white',
    violet: 'border-violet-200/70 from-violet-50 to-white',
    emerald: 'border-emerald-200/70 from-emerald-50 to-white',
    rose: 'border-rose-200/70 from-rose-50 to-white',
    amber: 'border-amber-200/70 from-amber-50 to-white',
  }

  const topBarClasses = {
    default: 'bg-slate-300',
    brand: 'bg-brand-500',
    violet: 'bg-violet-500',
    emerald: 'bg-emerald-500',
    rose: 'bg-rose-500',
    amber: 'bg-amber-500',
  }

  return (
    <div
      className={`relative overflow-hidden rounded-[26px] border bg-linear-to-br p-5 shadow-sm ${accentClasses[accent] || accentClasses.default}`}
    >
      <div
        className={`absolute inset-x-0 top-0 h-1.5 ${topBarClasses[accent] || topBarClasses.default}`}
      />

      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-3 wrap-break-word text-3xl font-semibold tracking-tight text-slate-950">
        {value}
      </p>

      {hint && <p className="mt-2 text-sm text-slate-400">{hint}</p>}
    </div>
  )
}