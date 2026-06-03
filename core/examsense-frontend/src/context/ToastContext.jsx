/*
ExamSense+ - Toast Context Provider
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste contextul global pentru notificari toast
- expune functiile necesare pentru afisarea si inchiderea toast-urilor
- randeaza lista de notificari active la nivelul intregii aplicatii
- gestioneaza inchiderea automata a toast-urilor dupa un interval scurt
*/

import { createContext, useCallback, useMemo, useState } from 'react'
import { X } from 'lucide-react'

export const ToastContext = createContext(null)

let idCounter = 1

// provider-ul pune la dispozitie functiile de toast pentru toata aplicatia
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  // stergem un toast dupa id
  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  // adaugam un toast nou si il inchidem automat dupa cateva secunde
  const showToast = useCallback((message, type = 'info') => {
    const id = idCounter++
    setToasts((prev) => [...prev, { id, message, type }])

    setTimeout(() => {
      removeToast(id)
    }, 3500)
  }, [removeToast])

  // expunem functiile de toast pentru restul aplicatiei
  const value = useMemo(
    () => ({ showToast, removeToast }),
    [showToast, removeToast]
  )

  return (
    <ToastContext.Provider value={value}>
      {children}

      {/* containerul global in care afisam toate notificarile active */}
      <div className="pointer-events-none fixed left-1/2 top-20 z-120 flex w-[calc(100%-1rem)] max-w-md -translate-x-1/2 flex-col gap-3 sm:left-auto sm:right-4 sm:top-4 sm:w-full sm:translate-x-0">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={`pointer-events-auto rounded-2xl border px-4 py-3 shadow-(--shadow-card) backdrop-blur-xl ${
              toast.type === 'success'
                ? 'border-emerald-200 bg-emerald-50/95 text-emerald-800'
                : toast.type === 'error'
                ? 'border-rose-200 bg-rose-50/95 text-rose-800'
                : 'border-slate-200 bg-white/95 text-slate-800'
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <p className="text-sm font-medium leading-6">{toast.message}</p>

              <button
                onClick={() => removeToast(toast.id)}
                className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-current/70 transition hover:bg-black/5 hover:text-current"
                aria-label="Închide notificarea"
              >
                <X size={16} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}