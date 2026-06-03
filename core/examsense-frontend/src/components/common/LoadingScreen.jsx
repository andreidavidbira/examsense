/*
ExamSense+ - Loading Screen Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste ecranul de loading afisat in faza initiala de incarcare a aplicatiei
- ofera un feedback vizual elegant in timpul initializarii
- foloseste animatie pentru o experienta mai fluida la pornirea interfetei
*/

import { motion } from 'framer-motion'

// afisam ecranul de incarcare al aplicatiei inainte ca datele esentiale sa fie gata
export default function LoadingScreen() {
  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="rounded-[28px] border border-white/60 bg-white/75 px-8 py-6 shadow-(--shadow-card) backdrop-blur-xl"
      >
        <div className="flex items-center gap-4">
          <div className="h-10 w-10 animate-pulse rounded-2xl bg-linear-to-br from-brand-500 to-violet-500" />
          <div>
            <p className="text-sm font-medium text-slate-500">ExamSense+</p>
            <p className="text-base font-semibold text-slate-900">Se încarcă aplicația...</p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}