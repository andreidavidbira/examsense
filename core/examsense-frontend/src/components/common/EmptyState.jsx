export default function EmptyState({
  title = 'Nu există date',
  description = 'Momentan nu există informații de afișat.',
  action = null,
}) {
  return (
    <div className="rounded-[28px] border border-dashed border-slate-200 bg-linear-to-br from-slate-50 to-white px-6 py-10 text-center shadow-xs">
      <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50 text-lg font-semibold text-brand-700">
        ∅
      </div>

      <h3 className="mt-5 text-lg font-semibold tracking-tight text-slate-950">
        {title}
      </h3>

      <p className="mx-auto mt-3 max-w-xl text-sm leading-7 text-slate-500">
        {description}
      </p>

      {action && <div className="mt-6 flex justify-center">{action}</div>}
    </div>
  )
}