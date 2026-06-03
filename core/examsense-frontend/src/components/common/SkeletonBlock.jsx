/*
ExamSense+ - Skeleton Block Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste componenta de baza pentru placeholder-ele de loading
- afiseaza un bloc simplu cu animatie de tip skeleton
- permite reutilizarea usoara in alte componente prin className
*/

// afisam un bloc placeholder simplu care poate fi refolosit in diverse zone ale interfetei
export default function SkeletonBlock({ className = '' }) {
  return <div className={`animate-pulse rounded-2xl bg-slate-200/70 ${className}`} />
}