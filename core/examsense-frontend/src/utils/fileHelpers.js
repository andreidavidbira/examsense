/*
ExamSense+ - File Display Helpers
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste functii helper pentru afisarea numelor de fisiere in frontend
- extrage numele fisierului dintr-un path complet sau URL
- pastreaza logica de formatare simpla si reutilizabila in componente
*/

// extragem doar numele fisierului dintr-un path complet
export function getDisplayFileName(filePath) {
  if (!filePath) {
    return ''
  }

  const normalized = String(filePath).replaceAll('\\', '/')
  const parts = normalized.split('/')

  return parts[parts.length - 1] || normalized
}