/*
ExamSense+ - Documents List Page
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste pagina care afiseaza documentele utilizatorului
- incarca lista documentelor existente din backend
- afiseaza stari pentru loading, eroare si lista goala
- permite navigarea catre pagina de upload si catre detaliile fiecarui document
*/

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import api from '../../api/axios'
import EmptyState from '../../components/common/EmptyState'
import ErrorAlert from '../../components/common/ErrorAlert'
import PageContainer from '../../components/common/PageContainer'
import Pagination from '../../components/common/Pagination'
import SectionCard from '../../components/common/SectionCard'
import SkeletonCard from '../../components/common/SkeletonCard'
import usePageTitle from '../../hooks/usePageTitle'
import { primaryButtonClass } from '../../utils/buttonClasses'
import { formatDateTime } from '../../utils/dateFormat'
import { getDisplayFileName } from '../../utils/fileHelpers'

const PAGE_SIZE = 10

// afisam lista documentelor utilizatorului curent
export default function DocumentsPage() {
  usePageTitle('Documentele mele')

  const [documents, setDocuments] = useState([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    // incarcam doar pagina curenta, nu toate documentele utilizatorului
    async function fetchDocuments() {
      try {
        setLoading(true)
        setError('')

        const response = await api.get('/documents/', {
          params: {
            page,
            page_size: PAGE_SIZE,
          },
        })

        setDocuments(response.data.results || [])
        setTotalPages(response.data.total_pages || 1)
        setTotalCount(response.data.count || 0)
      } catch {
        setError('Nu am putut încărca documentele.')
      } finally {
        setLoading(false)
      }
    }

    fetchDocuments()
  }, [page])

  return (
    <PageContainer>
      <SectionCard
        title="Documentele mele"
        subtitle="Gestionează materialele încărcate și deschide documentele procesate."
        rightSlot={
          <Link
            to="/documents/upload"
            className={`inline-flex items-center justify-center ${primaryButtonClass}`}
          >
            Încarcă document
          </Link>
        }
      >
        {loading ? (
          <div className="grid gap-4 lg:grid-cols-2">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
        ) : error ? (
          <ErrorAlert message={error} />
        ) : totalCount === 0 ? (
          <EmptyState
            title="Nu există documente"
            description="Încarcă primul document pentru a genera definiții și întrebări."
          />
        ) : (
          <>
            <div className="grid gap-4 lg:grid-cols-2">
              {documents.map((doc) => (
                <Link
                  key={doc.id}
                  to={`/documents/${doc.id}`}
                  className="min-w-0 overflow-hidden rounded-3xl border border-slate-200/80 bg-white/90 p-5 shadow-sm transition hover:border-brand-200 hover:bg-brand-50/40 hover:shadow-md"
                >
                  <p className="text-sm text-slate-500">
                    Document #{doc.user_document_number}
                  </p>

                  <p className="mt-2 min-w-0 break-all text-lg font-semibold leading-7 text-slate-950">
                    {getDisplayFileName(doc.file)}
                  </p>

                  <p className="mt-3 text-sm text-slate-500">
                    {formatDateTime(doc.uploaded_at)}
                  </p>
                </Link>
              ))}
            </div>

            <Pagination
              page={page}
              totalPages={totalPages}
              onChange={setPage}
            />
          </>
        )}
      </SectionCard>
    </PageContainer>
  )
}
