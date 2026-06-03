/*
ExamSense+ - Page Loader Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste componenta reutilizabila pentru afisarea starii de loading
- afiseaza un indicator vizual de incarcare si un text explicativ
- mentine consistenta interfetei in paginile care asteapta date din backend
*/

// afisam un loader standard pentru paginile sau sectiunile care se incarca
export default function PageLoader({ text = 'Se încarcă...' }) {
  return (
    <div className="flex min-h-60 flex-col items-center justify-center rounded-[28px] border border-slate-200 bg-white px-6 py-12 shadow-sm">
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-slate-200 border-t-brand-500" />
      <p className="mt-5 text-sm font-medium text-slate-500">{text}</p>
    </div>
  )
}