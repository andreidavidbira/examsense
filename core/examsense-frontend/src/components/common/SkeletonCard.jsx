import SkeletonBlock from './SkeletonBlock'

export default function SkeletonCard() {
  return (
    <div className="rounded-[24px] border border-slate-200/70 bg-white/90 p-5 shadow-sm">
      <SkeletonBlock className="h-4 w-24" />
      <SkeletonBlock className="mt-4 h-7 w-40" />
      <SkeletonBlock className="mt-3 h-4 w-32" />
    </div>
  )
}