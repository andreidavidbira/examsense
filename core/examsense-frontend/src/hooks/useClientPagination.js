/*
ExamSense+ - Client Pagination Hook
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste un hook reutilizabil pentru paginarea locala a listelor
- imparte elementele primite in pagini de dimensiune fixa
- recentreaza pagina curenta atunci cand lista se modifica si pagina selectata nu mai este valida
*/

import { useEffect, useMemo, useState } from 'react'

// impartim local o lista in pagini, fara sa modificam datele originale
export default function useClientPagination(items, pageSize = 10) {
  const [page, setPage] = useState(1)

  const safeItems = Array.isArray(items) ? items : []

  const totalPages = Math.max(1, Math.ceil(safeItems.length / pageSize))

  const paginatedItems = useMemo(() => {
    const start = (page - 1) * pageSize
    const end = start + pageSize

    return safeItems.slice(start, end)
  }, [safeItems, page, pageSize])

  // daca lista se scurteaza si pagina curenta nu mai exista, revenim la ultima pagina valida
  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages)
    }
  }, [page, totalPages])

  return {
    page,
    totalPages,
    paginatedItems,
    setPage,
  }
}