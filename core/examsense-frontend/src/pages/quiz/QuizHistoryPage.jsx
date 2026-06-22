/*
ExamSense+ - Quiz History Page
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste pagina care afiseaza istoricul quiz-urilor finalizate
- incarca lista attempt-urilor rezolvate de utilizator
- permite reluarea unui quiz, generarea unuia nou si accesul la detalii
- afiseaza informatii relevante despre scoruri, timp si comparatia user vs AI
*/

import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import api from '../../api/axios'
import EmptyState from '../../components/common/EmptyState'
import PageContainer from '../../components/common/PageContainer'
import Pagination from '../../components/common/Pagination'
import QuizOptionsDialog from '../../components/common/QuizOptionsDialog'
import SectionCard from '../../components/common/SectionCard'
import useClientPagination from '../../hooks/useClientPagination'
import usePageTitle from '../../hooks/usePageTitle'
import { useToast } from '../../hooks/useToast'
import {
  primaryButtonClass,
  secondaryButtonClass,
} from '../../utils/buttonClasses'
import { formatDateTime } from '../../utils/dateFormat'
import { formatDuration } from '../../utils/timeFormat'

// alegem stilul badge-ului in functie de metoda prin care a fost generat quiz-ul
function modeBadgeClass(mode) {
  return mode === 'ai'
    ? 'rounded-full bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700'
    : 'rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700'
}

// afisam istoricul attempt-urilor finalizate si actiunile posibile pentru fiecare
export default function QuizHistoryPage() {
  usePageTitle('Istoric quiz-uri')

  const navigate = useNavigate()
  const { showToast } = useToast()

  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [selectedDocumentId, setSelectedDocumentId] = useState(null)
  const [selectedGenerationMode, setSelectedGenerationMode] = useState('nlp')
  const [quizOptionsOpen, setQuizOptionsOpen] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  // lista completa de attempt-uri primita de la backend
  const attempts = data?.results || []

  // impartim istoricul in pagini de maximum 10 attempt-uri
  const {
    page,
    totalPages,
    paginatedItems: paginatedAttempts,
    setPage,
  } = useClientPagination(attempts, 10)

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

  function handleReplaySame(questionSetId) {
    navigate(`/quiz/${questionSetId}`)
  }

  function openGenerateDialog(documentId, generationMode) {
    setSelectedDocumentId(documentId)
    setSelectedGenerationMode(generationMode || 'nlp')
    setQuizOptionsOpen(true)
  }

  async function handleGenerateNewQuiz(options) {
    if (!selectedDocumentId) return

    try {
      setIsGenerating(true)

      const response = await api.post(
        `/documents/${selectedDocumentId}/regenerate-questions/`,
        {
          difficulty: options.difficulty,
          max_questions: options.max_questions,
          generation_mode: options.generation_mode,
        },
        {
          timeout: 120000,
        }
      )

      showToast('A fost generat un nou set de întrebări.', 'success')
      navigate(`/quiz/${response.data.question_set_id}`)
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
        description="Alege metoda, dificultatea și numărul de întrebări pentru noul quiz."
        confirmText="Generează"
        cancelText="Anulează"
        initialDifficulty="medium"
        initialMaxQuestions={10}
        initialGenerationMode={selectedGenerationMode}
        isSubmitting={isGenerating}
        onConfirm={handleGenerateNewQuiz}
        onCancel={() => setQuizOptionsOpen(false)}
      />

      <SectionCard
        title="Istoric quiz-uri"
        subtitle="Toate quiz-urile finalizate până acum."
      >
        {attempts.length === 0 ? (
          <EmptyState
            title="Nu există quiz-uri finalizate"
            description="Completează un quiz pentru a vedea istoricul aici."
          />
        ) : (
          <>
            <div className="grid gap-4">
              {paginatedAttempts.map((attempt) => (
                <div
                  key={attempt.id}
                  className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-brand-200 hover:shadow-md"
                >
                  <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-sm text-slate-500">
                          Attempt #{attempt.user_attempt_number}
                        </p>

                        <span className={modeBadgeClass(attempt.generation_mode)}>
                          {String(attempt.generation_mode).toUpperCase()}
                        </span>
                      </div>

                      <p className="mt-2 text-base font-semibold text-slate-950">
                        Document #{attempt.user_document_number}
                      </p>

                      <div className="mt-3 grid gap-2 sm:grid-cols-2">
                        <p className="text-sm text-slate-500">
                          {formatDateTime(attempt.completed_at)}
                        </p>

                        <p className="text-sm text-slate-500">
                          Timp user: {formatDuration(attempt.time_spent_seconds)}
                        </p>

                        {attempt.ai_attempt && (
                          <p className="text-sm text-slate-500">
                            Timp AI:{' '}
                            {formatDuration(
                              attempt.ai_attempt.time_spent_seconds
                            )}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex w-full flex-col gap-3 xl:w-auto xl:items-end">
                      <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 xl:text-right">
                        <p className="text-base font-semibold text-slate-950">
                          User: {attempt.score} / {attempt.total_questions}
                        </p>

                        {attempt.ai_attempt && (
                          <p className="mt-1 text-sm text-slate-500">
                            AI: {attempt.ai_attempt.score} /{' '}
                            {attempt.ai_attempt.total_questions}
                          </p>
                        )}
                      </div>

                      <div className="grid gap-2 sm:grid-cols-3 xl:flex">
                        <Link
                          to={`/quiz-history/${attempt.id}`}
                          className={secondaryButtonClass}
                        >
                          Detalii
                        </Link>

                        {attempt.question_set_id && (
                          <button
                            type="button"
                            onClick={() =>
                              handleReplaySame(attempt.question_set_id)
                            }
                            className={secondaryButtonClass}
                          >
                            Reia același quiz
                          </button>
                        )}

                        <button
                          type="button"
                          onClick={() =>
                            openGenerateDialog(
                              attempt.document,
                              attempt.generation_mode
                            )
                          }
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