/*
ExamSense+ - Pagination Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste componenta comuna de paginare folosita in listele din frontend
- afiseaza doar paginile relevante, cu puncte de suspensie intre intervale
- permite navigarea la prima pagina, pagina anterioara, pagina urmatoare si ultima pagina
*/

function getPageItems(currentPage, totalPages) {
  const pages = []

  if (totalPages <= 7) {
    for (let i = 1; i <= totalPages; i++) {
      pages.push(i)
    }

    return pages
  }

  pages.push(1)

  if (currentPage > 4) {
    pages.push('left-ellipsis')
  }

  const startPage = Math.max(2, currentPage - 1)
  const endPage = Math.min(totalPages - 1, currentPage + 1)

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }

  if (currentPage < totalPages - 3) {
    pages.push('right-ellipsis')
  }

  pages.push(totalPages)

  return pages
}

// afisam o paginare compacta, potrivita pentru liste mari
export default function Pagination({ page, totalPages, onChange }) {
  if (totalPages <= 1) return null

  const pageItems = getPageItems(page, totalPages)

  function goToPage(pageNumber) {
    if (pageNumber < 1 || pageNumber > totalPages || pageNumber === page) {
      return
    }

    onChange(pageNumber)
  }

  const buttonClass =
    'rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-40'

  const activeButtonClass =
    'rounded-xl bg-slate-950 px-3 py-2 text-sm font-medium text-white transition'

  return (
    <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
      <button
        type="button"
        onClick={() => goToPage(1)}
        disabled={page === 1}
        className={buttonClass}
        title="Prima pagina"
      >
        «
      </button>

      <button
        type="button"
        onClick={() => goToPage(page - 1)}
        disabled={page === 1}
        className={buttonClass}
        title="Pagina anterioara"
      >
        ‹
      </button>

      {pageItems.map((item) => {
        if (typeof item === 'string') {
          return (
            <span
              key={item}
              className="flex min-w-10 items-center justify-center px-2 py-2 text-sm font-medium text-slate-400"
            >
              ...
            </span>
          )
        }

        return (
          <button
            key={item}
            type="button"
            onClick={() => goToPage(item)}
            className={item === page ? activeButtonClass : buttonClass}
          >
            {item}
          </button>
        )
      })}

      <button
        type="button"
        onClick={() => goToPage(page + 1)}
        disabled={page === totalPages}
        className={buttonClass}
        title="Pagina urmatoare"
      >
        ›
      </button>

      <button
        type="button"
        onClick={() => goToPage(totalPages)}
        disabled={page === totalPages}
        className={buttonClass}
        title="Ultima pagina"
      >
        »
      </button>
    </div>
  )
}