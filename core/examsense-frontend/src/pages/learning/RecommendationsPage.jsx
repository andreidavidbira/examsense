import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import api from '../../api/axios'
import EmptyState from '../../components/common/EmptyState'
import PageContainer from '../../components/common/PageContainer'
import PageLoader from '../../components/common/PageLoader'
import SectionCard from '../../components/common/SectionCard'
import { primaryButtonClass, secondaryButtonClass } from '../../utils/buttonClasses'
import usePageTitle from '../../hooks/usePageTitle'

function getPriorityStyle(wrongCount) {
  if (wrongCount >= 5) {
    return {
      badge: 'rounded-full bg-rose-100 px-3 py-1 text-xs font-semibold text-rose-700',
      card: 'border-rose-200 bg-rose-50/70',
      label: 'Prioritate ridicată',
    }
  }

  if (wrongCount >= 3) {
    return {
      badge: 'rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700',
      card: 'border-amber-200 bg-amber-50/70',
      label: 'Prioritate medie',
    }
  }

  return {
    badge: 'rounded-full bg-brand-100 px-3 py-1 text-xs font-semibold text-brand-700',
    card: 'border-brand-200 bg-brand-50/70',
    label: 'Consolidare',
  }
}

export default function RecommendationsPage() {
  usePageTitle('Recomandări de învățare')

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
        <PageLoader text="Se încarcă recomandările..." />
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <div className="space-y-6">
        <SectionCard
          title="Recomandări de învățare"
          subtitle="Concepte la care ai greșit frecvent, împreună cu definiția lor și o recomandare clară de recapitulare."
          rightSlot={
            <div className="flex flex-wrap gap-2">
              <Link to="/weak-concepts" className={secondaryButtonClass}>
                Vezi conceptele slabe
              </Link>
              <Link to="/retry-quiz" className={primaryButtonClass}>
                Quiz de recapitulare
              </Link>
            </div>
          }
        >
          {data.results.length === 0 ? (
            <EmptyState
              title="Nu există recomandări"
              description="Fă mai multe quiz-uri pentru a genera recomandări utile."
            />
          ) : (
            <div className="grid gap-4">
              {data.results.map((item, index) => {
                const priority = getPriorityStyle(item.wrong_count)

                return (
                  <div
                    key={`${item.concept}-${index}`}
                    className={`rounded-[26px] border p-5 shadow-sm ${priority.card}`}
                  >
                    <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="text-xl font-semibold tracking-tight text-slate-950">
                            {item.concept}
                          </p>
                          <span className={priority.badge}>{priority.label}</span>
                        </div>

                        <p className="mt-3 text-sm text-slate-500">
                          Greșit de {item.wrong_count} ori
                        </p>

                        {item.user_document_number && (
                          <p className="mt-2 text-xs text-slate-400">
                            Asociat documentului #{item.user_document_number}
                          </p>
                        )}
                      </div>

                      <div className="shrink-0">
                        <span className="rounded-full bg-white/80 px-3 py-1 text-xs font-medium text-slate-700">
                          Recapitulare recomandată
                        </span>
                      </div>
                    </div>

                    <div className="mt-5 grid gap-4 lg:grid-cols-[1fr_1fr]">
                      <div className="rounded-2xl border border-slate-200 bg-white/90 p-4">
                        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                          Definiție
                        </p>
                        <p className="mt-3 text-sm leading-7 text-slate-700">
                          {item.definition || 'Definiția nu este disponibilă pentru acest concept.'}
                        </p>
                      </div>

                      <div className="rounded-2xl border border-slate-200 bg-white/90 p-4">
                        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                          Recomandare
                        </p>
                        <p className="mt-3 text-sm leading-7 text-slate-700">
                          {item.recommendation}
                        </p>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </SectionCard>
      </div>
    </PageContainer>
  )
}