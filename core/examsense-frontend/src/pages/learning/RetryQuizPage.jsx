import { useEffect, useState } from 'react'
import api from '../../api/axios'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import EmptyState from '../../components/common/EmptyState'

export default function RetryQuizPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchRetryQuiz() {
      try {
        const response = await api.post('/learning/retry-quiz/')
        setData(response.data)
      } catch {
        setError('Nu am putut genera quiz-ul de recapitulare.')
      }
    }

    fetchRetryQuiz()
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
        <p className="text-sm text-slate-500">Se încarcă quiz-ul de recapitulare...</p>
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <SectionCard
        title="Quiz de recapitulare"
        subtitle="Întrebări generate din conceptele la care ai greșit mai des."
      >
        {data.questions.length === 0 ? (
          <EmptyState
            title="Nu există suficiente date pentru recapitulare"
            description={
              data.message || 'Mai fă quiz-uri pentru a genera întrebări de recapitulare.'
            }
          />
        ) : (
          <div className="grid gap-4">
            {data.questions.map((question) => (
              <div
                key={question.id}
                className="rounded-2xl border border-slate-200 bg-white p-4"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                    {question.question_type}
                  </span>
                  <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
                    {question.language.toUpperCase()}
                  </span>
                </div>

                <p className="mt-3 text-sm font-medium text-slate-900">
                  {question.question_text}
                </p>

                {Array.isArray(question.options) && question.options.length > 0 && (
                  <div className="mt-3 grid gap-2">
                    {question.options.map((option, index) => (
                      <div
                        key={`${question.id}-option-${index}`}
                        className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700"
                      >
                        {option}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </SectionCard>
    </PageContainer>
  )
}