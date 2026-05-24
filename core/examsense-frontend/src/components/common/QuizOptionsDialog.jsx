import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { primaryButtonClass, secondaryButtonClass } from '../../utils/buttonClasses'

export default function QuizOptionsDialog({
  open,
  title = 'Configurează quiz-ul',
  description = 'Alege dificultatea și numărul de întrebări.',
  confirmText = 'Generează quiz',
  cancelText = 'Anulează',
  initialDifficulty = 'medium',
  initialMaxQuestions = 10,
  isSubmitting = false,
  onConfirm,
  onCancel,
}) {
  const [difficulty, setDifficulty] = useState(initialDifficulty)
  const [maxQuestions, setMaxQuestions] = useState(initialMaxQuestions)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (open) {
      setDifficulty(initialDifficulty)
      setMaxQuestions(initialMaxQuestions)
      setErrors({})
    }
  }, [open, initialDifficulty, initialMaxQuestions])

  function validate() {
    const newErrors = {}

    const numericValue = Number(maxQuestions)

    if (!difficulty) {
      newErrors.difficulty = 'Selectează dificultatea.'
    }

    if (!numericValue) {
      newErrors.maxQuestions = 'Numărul de întrebări este obligatoriu.'
    } else if (numericValue < 1) {
      newErrors.maxQuestions = 'Numărul minim de întrebări este 1.'
    } else if (numericValue > 30) {
      newErrors.maxQuestions = 'Numărul maxim de întrebări este 30.'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  function handleConfirm() {
    if (!validate()) {
      return
    }

    onConfirm({
      difficulty,
      max_questions: Number(maxQuestions),
    })
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            className="fixed inset-0 z-[90] bg-slate-950/35 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onCancel}
          />

          <motion.div
            className="fixed inset-0 z-[100] flex items-center justify-center p-4"
            initial={{ opacity: 0, scale: 0.96, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 10 }}
          >
            <div className="w-full max-w-md rounded-[28px] border border-white/60 bg-white p-6 shadow-2xl">
              <h3 className="text-xl font-semibold tracking-tight text-slate-950">{title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>

              <div className="mt-6 space-y-4">
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">
                    Dificultate
                  </label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                  {errors.difficulty && (
                    <p className="mt-2 text-xs text-rose-600">{errors.difficulty}</p>
                  )}
                </div>

                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-700">
                    Număr întrebări
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="30"
                    value={maxQuestions}
                    onChange={(e) => setMaxQuestions(e.target.value)}
                    className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  />
                  {errors.maxQuestions && (
                    <p className="mt-2 text-xs text-rose-600">{errors.maxQuestions}</p>
                  )}
                </div>
              </div>

              <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-end">
                <button onClick={onCancel} className={secondaryButtonClass}>
                  {cancelText}
                </button>
                <button onClick={handleConfirm} className={primaryButtonClass} disabled={isSubmitting}>
                  {isSubmitting ? 'Se generează...' : confirmText}
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}