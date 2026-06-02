export default function PageLoader({ text = 'Se încarcă...' }) {
  return (
    <div className="flex min-h-[240px] flex-col items-center justify-center rounded-[28px] border border-slate-200 bg-white px-6 py-12 shadow-sm">
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-slate-200 border-t-brand-500" />
      <p className="mt-5 text-sm font-medium text-slate-500">{text}</p>
    </div>
  )
}