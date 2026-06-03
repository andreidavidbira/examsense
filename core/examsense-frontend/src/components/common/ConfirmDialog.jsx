/*
ExamSense+ - Confirm Dialog Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste dialogul reutilizabil pentru confirmarile din interfata
- afiseaza un mesaj clar inaintea actiunilor sensibile sau ireversibile
- permite alegerea stilului butonului de confirmare in functie de tipul actiunii
- foloseste animatii pentru aparitia si disparitia dialogului
*/

import { motion, AnimatePresence } from 'framer-motion'
import { primaryButtonClass, secondaryButtonClass, dangerButtonClass } from '../../utils/buttonClasses'

// afisam un dialog modal pentru confirmarile explicite ale utilizatorului
export default function ConfirmDialog({
  open,
  title = 'Confirmare',
  description = 'Ești sigur?',
  confirmText = 'Confirmă',
  cancelText = 'Anulează',
  onConfirm,
  onCancel,
  variant = 'danger',
}) {
  // alegem stilul butonului principal in functie de tipul actiunii confirmate
  const confirmClass = variant === 'danger' ? dangerButtonClass : primaryButtonClass

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 z-90 bg-slate-950/35 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onCancel}
          />

          <motion.div
            className="fixed inset-0 z-100 flex items-center justify-center p-4"
            initial={{ opacity: 0, scale: 0.96, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 10 }}
          >
            <div className="w-full max-w-md rounded-[28px] border border-white/60 bg-white p-6 shadow-2xl">
              <h3 className="text-xl font-semibold tracking-tight text-slate-950">{title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>

              <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-end">
                <button onClick={onCancel} className={secondaryButtonClass}>
                  {cancelText}
                </button>
                <button onClick={onConfirm} className={confirmClass}>
                  {confirmText}
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}