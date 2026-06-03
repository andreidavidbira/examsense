/*
ExamSense+ - Skeleton Card Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste un card placeholder pentru starea de loading
- afiseaza o structura vizuala temporara pana la incarcarea datelor reale
- mentine consistenta layout-ului in paginile care folosesc carduri
*/

import SkeletonBlock from './SkeletonBlock'

// afisam un card placeholder cat timp datele reale sunt inca la incarcare
export default function SkeletonCard() {
  return (
    <div className="rounded-3xl border border-slate-200/70 bg-white/90 p-5 shadow-sm">
      <SkeletonBlock className="h-4 w-24" />
      <SkeletonBlock className="mt-4 h-7 w-40" />
      <SkeletonBlock className="mt-3 h-4 w-32" />
    </div>
  )
}