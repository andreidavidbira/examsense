export default function PageLoader({ text = 'Se încarcă...' }) {
  return (
    <div className="flex min-h-[220px] flex-col items-center justify-center gap-4 rounded-[28px] border border-slate-200 bg-white/80 p-8 shadow-sm">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900" />
      <p className="text-sm font-medium text-slate-500">{text}</p>
    </div>
  )
}