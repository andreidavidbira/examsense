import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import EmptyState from '../../components/common/EmptyState'
import QuizOptionsDialog from '../../components/common/QuizOptionsDialog'
import { useToast } from '../../hooks/useToast'
import { primaryButtonClass, secondaryButtonClass } from '../../utils/buttonClasses'

export default function QuizHistoryPage() {
  const navigate = useNavigate()
  const { showToast } = useToast()

  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [selectedDocumentId, setSelectedDocumentId] = useState(null)
  const [quizOptionsOpen, setQuizOptionsOpen] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    async function fetchHistory() {
      try {
        const response = await api.get('/documents/quiz-history/')
        setData(response.data)
      } catch {
        setError('Nu am putut încărca istoricul quiz-urilor.')
      }
    }

    fetchHistory()
  }, [])

  function handleReplaySame(documentId) {
    navigate(`/documents/${documentId}/quiz`)
  }

  function openGenerateDialog(documentId) {
    setSelectedDocumentId(documentId)
    setQuizOptionsOpen(true)
  }

  async function handleGenerateNewQuiz(options) {
    if (!selectedDocumentId) return

    try {
      setIsGenerating(true)

      await api.post(`/documents/${selectedDocumentId}/regenerate-questions/`, {
        difficulty: options.difficulty,
        max_questions: options.max_questions,
      })

      showToast('A fost generat un nou set de întrebări.', 'success')
      navigate(`/documents/${selectedDocumentId}/quiz`)
    } catch {
      showToast('Nu am putut genera un nou quiz.', 'error')
    } finally {
      setIsGenerating(false)
      setQuizOptionsOpen(false)
      setSelectedDocumentId(null)
    }
  }

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
        <p className="text-sm text-slate-500">Se încarcă istoricul...</p>
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <QuizOptionsDialog
        open={quizOptionsOpen}
        title="Generează alt quiz"
        description="Alege dificultatea și numărul de întrebări pentru noul quiz."
        confirmText="Generează"
        cancelText="Anulează"
        initialDifficulty="medium"
        initialMaxQuestions={10}
        isSubmitting={isGenerating}
        onConfirm={handleGenerateNewQuiz}
        onCancel={() => setQuizOptionsOpen(false)}
      />

      <SectionCard
        title="Istoric quiz-uri"
        subtitle="Toate quiz-urile finalizate până acum."
      >
        {data.results.length === 0 ? (
          <EmptyState
            title="Nu există quiz-uri finalizate"
            description="Completează un quiz pentru a vedea istoricul aici."
          />
        ) : (
          <div className="grid gap-4">
            {data.results.map((attempt) => (
              <div
                key={attempt.id}
                className="rounded-2xl border border-slate-200 bg-white p-4 transition hover:shadow-sm"
              >
                <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                  <div>
                    <p className="text-sm text-slate-500">Attempt #{attempt.user_attempt_number}</p>
                    <p className="mt-1 text-base font-semibold text-slate-950">
                      Document #{attempt.user_document_number}
                    </p>
                    <p className="mt-2 text-sm text-slate-500">
                      {new Date(attempt.completed_at).toLocaleString()}
                    </p>
                  </div>

                  <div className="flex flex-col gap-3 lg:items-end">
                    <p className="text-base font-semibold text-slate-950">
                      {attempt.score} / {attempt.total_questions}
                    </p>

                    <div className="flex flex-wrap gap-2">
                      <Link
                        to={`/quiz-history/${attempt.id}`}
                        className={secondaryButtonClass}
                      >
                        Detalii
                      </Link>

                      <button
                        onClick={() => handleReplaySame(attempt.document)}
                        className={secondaryButtonClass}
                      >
                        Reia același quiz
                      </button>

                      <button
                        onClick={() => openGenerateDialog(attempt.document)}
                        className={primaryButtonClass}
                      >
                        Quiz nou
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </SectionCard>
    </PageContainer>
  )
}