import { useEffect, useState } from 'react'
import api from '../../api/axios'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import EmptyState from '../../components/common/EmptyState'

export default function RecommendationsPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchRecommendations() {
      try {
        const response = await api.get('/learning/recommendations/')
        setData(response.data)
      } catch {
        setError('Nu am putut încărca recomandările.')
      }
    }

    fetchRecommendations()
  }, [])

  if (error) {
    return (
      <PageContainer>
        <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      </PageContainer>
    )
  }

  if (!data) {
    return (
      <PageContainer>
        <p className="text-sm text-slate-500">Se încarcă recomandările...</p>
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <SectionCard
        title="Recomandări"
        subtitle="Concepte prioritare pentru recapitulare, pe baza greșelilor recurente."
      >
        {data.results.length === 0 ? (
          <EmptyState
            title="Nu există recomandări"
            description="Fă mai multe quiz-uri pentru a genera recomandări utile."
          />
        ) : (
          <div className="grid gap-4">
            {data.results.map((item, index) => (
              <div
                key={`${item.concept}-${index}`}
                className="rounded-2xl border border-slate-200 bg-white p-4"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-lg font-semibold text-slate-950">{item.concept}</p>
                    <p className="mt-2 text-sm text-slate-500">
                      Greșit de {item.wrong_count} ori
                    </p>
                  </div>

                  {item.user_document_number && (
                    <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
                      Document #{item.user_document_number}
                    </span>
                  )}
                </div>

                <p className="mt-4 text-sm leading-6 text-slate-700">
                  {item.recommendation}
                </p>
              </div>
            ))}
          </div>
        )}
      </SectionCard>
    </PageContainer>
  )
}