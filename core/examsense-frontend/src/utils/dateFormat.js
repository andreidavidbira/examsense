/*
ExamSense+ - Date Formatting Helpers
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste functii helper pentru formatarea datelor afisate in frontend
- transforma valorile brute de tip data intr-un format romanesc unitar
- separa afisarea completa data + ora de afisarea simpla doar a datei
*/

// formateaza data si ora intr-un format usor de citit pentru interfata
export function formatDateTime(value) {
  if (!value) return '-'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return '-'
  }

  return date.toLocaleString('ro-RO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// formateaza doar data, fara afisarea orei
export function formatDateOnly(value) {
  if (!value) return '-'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return '-'
  }

  return date.toLocaleDateString('ro-RO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}