import { useEffect, useState } from 'react'
import api from '../../api/axios'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import EmptyState from '../../components/common/EmptyState'

export default function WeakConceptsPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchWeakConcepts() {
      try {
        const response = await api.get('/learning/weak-concepts/')
        setData(response.data)
      } catch {
        setError('Nu am putut încărca conceptele slabe.')
      }
    }

    fetchWeakConcepts()
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
        <p className="text-sm text-slate-500">Se încarcă...</p>
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <SectionCard
        title="Concepte slabe"
        subtitle="Zonele unde ai nevoie de exersare și recapitulare suplimentară."
      >
        {data.results.length === 0 ? (
          <EmptyState
            title="Nu există concepte slabe"
            description="Mai întâi trebuie să finalizezi câteva quiz-uri."
          />
        ) : (
          <div className="grid gap-4">
            {data.results.map((item, index) => (
              <div
                key={`${item.concept}-${index}`}
                className="rounded-2xl border border-slate-200 bg-white p-4"
              >
                <p className="text-lg font-semibold text-slate-950">{item.concept}</p>
                <p className="mt-2 text-sm text-slate-500">
                  Greșit de {item.wrong_count} ori
                </p>

                {item.document_id && (
                  <p className="mt-2 text-xs text-slate-400">
                    Asociat documentului #{item.document_id}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </SectionCard>
    </PageContainer>
  )
}