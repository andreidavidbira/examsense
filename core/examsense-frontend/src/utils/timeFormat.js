/*
ExamSense+ - Time Formatting Helpers
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste functii helper pentru formatarea duratelor afisate in frontend
- transforma valorile exprimate in secunde intr-un format usor de citit
- este folosit pentru afisarea timpului petrecut de utilizator sau de AI
*/

// formateaza o durata exprimata in secunde intr-o varianta mai usor de citit
export function formatDuration(seconds) {
  const safeSeconds = Math.max(0, Number(seconds || 0))

  const hours = Math.floor(safeSeconds / 3600)
  const minutes = Math.floor((safeSeconds % 3600) / 60)
  const secs = safeSeconds % 60

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  }

  if (minutes > 0) {
    return `${minutes}m ${secs}s`
  }

  return `${secs}s`
}