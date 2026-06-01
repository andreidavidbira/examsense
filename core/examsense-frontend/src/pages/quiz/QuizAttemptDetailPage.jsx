import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import api from '../../api/axios'
import EmptyState from '../../components/common/EmptyState'
import PageContainer from '../../components/common/PageContainer'
import QuizOptionsDialog from '../../components/common/QuizOptionsDialog'
import SectionCard from '../../components/common/SectionCard'
import { useToast } from '../../hooks/useToast'
import usePageTitle from '../../hooks/usePageTitle'
import {
  primaryButtonClass,
  secondaryButtonClass,
} from '../../utils/buttonClasses'
import { formatDuration } from '../../utils/timeFormat'

function modeBadgeClass(mode) {
  return mode === 'ai'
    ? 'rounded-full bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700'
    : 'rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700'
}

export default function QuizAttemptDetailPage() {
  usePageTitle('Detalii încercare quiz')

  const { attemptId } = useParams()
  const navigate = useNavigate()
  const { showToast } = useToast()

  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [quizOptionsOpen, setQuizOptionsOpen] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  useEffect(() => {
    async function fetchAttempt() {
      try {
        const response = await api.get(`/documents/quiz-history/${attemptId}/`)
        setData(response.data)
      } catch {
        setError('Nu am putut încărca detaliile quiz-ului.')
      }
    }

    fetchAttempt()
  }, [attemptId])

  const aiAnswerMap = useMemo(() => {
    const map = {}
    const aiAnswers = data?.ai_attempt?.answers || []

    aiAnswers.forEach((answer) => {
      map[answer.question.id] = answer
    })

    return map
  }, [data])

  function handleReplaySameQuiz() {
    if (!data?.question_set_id) return
    navigate(`/quiz/${data.question_set_id}`)
  }

  async function handleGenerateNewQuiz(options) {
    if (!data) return

    try {
      setIsGenerating(true)

      const response = await api.post(
        `/documents/${data.document}/regenerate-questions/`,
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
        <p className="text-sm text-slate-500">Se încarcă detaliile...</p>
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
        initialGenerationMode={data.generation_mode || 'nlp'}
        isSubmitting={isGenerating}
        onConfirm={handleGenerateNewQuiz}
        onCancel={() => setQuizOptionsOpen(false)}
      />

      <div className="space-y-6">
        <SectionCard
          title={`Attempt #${data.user_attempt_number}`}
          subtitle={`Scor user: ${data.score} / ${data.total_questions}`}
          rightSlot={
            <div className="grid w-full gap-2 sm:w-auto sm:grid-cols-2 lg:flex">
              {data.question_set_id && (
                <button onClick={handleReplaySameQuiz} className={secondaryButtonClass}>
                  Reia același quiz
                </button>
              )}

              <button
                onClick={() => setQuizOptionsOpen(true)}
                className={primaryButtonClass}
              >
                Quiz nou
              </button>

              <Link to="/quiz-history" className={secondaryButtonClass}>
                Înapoi la istoric
              </Link>
            </div>
          }
        >
          <div className="mb-5 flex flex-wrap items-center gap-2">
            <span className={modeBadgeClass(data.generation_mode)}>
              {String(data.generation_mode).toUpperCase()}
            </span>

            {data.question_set_id && (
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                Set #{data.question_set_id}
              </span>
            )}
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Document</p>
              <p className="mt-2 text-lg font-semibold text-slate-950">
                #{data.user_document_number}
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Finalizat la</p>
              <p className="mt-2 text-sm font-medium text-slate-900">
                {new Date(data.completed_at).toLocaleString()}
              </p>
            </div>

            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4">
              <p className="text-sm text-amber-700">Timp user</p>
              <p className="mt-2 text-lg font-semibold text-slate-950">
                {formatDuration(data.time_spent_seconds)}
              </p>
            </div>

            <div className="rounded-2xl border border-violet-200 bg-violet-50 p-4">
              <p className="text-sm text-violet-700">Timp AI</p>
              <p className="mt-2 text-lg font-semibold text-slate-950">
                {data.ai_attempt ? formatDuration(data.ai_attempt.time_spent_seconds) : '-'}
              </p>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="Răspunsuri"
          subtitle="Revizuirea completă a încercării și comparația cu AI."
        >
          {data.answers.length === 0 ? (
            <EmptyState
              title="Nu există răspunsuri"
              description="Această încercare nu conține răspunsuri salvate."
            />
          ) : (
            <div className="grid gap-4">
              {data.answers.map((answer) => {
                const aiAnswer = aiAnswerMap[answer.question.id]

                return (
                  <div
                    key={answer.id}
                    className={`rounded-3xl border p-4 sm:p-5 ${
                      answer.is_correct
                        ? 'border-emerald-200 bg-emerald-50/80'
                        : 'border-rose-200 bg-rose-50/80'
                    }`}
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                        {answer.question.question_type}
                      </span>
                      <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
                        {answer.question.language.toUpperCase()}
                      </span>
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-semibold ${
                          answer.is_correct
                            ? 'bg-emerald-100 text-emerald-700'
                            : 'bg-rose-100 text-rose-700'
                        }`}
                      >
                        {answer.is_correct ? 'Corect' : 'Greșit'}
                      </span>
                    </div>

                    <p className="mt-4 wrap-break-word text-sm font-medium leading-7 text-slate-900">
                      {answer.question.question_text}
                    </p>

                    <div className="mt-4 grid gap-3 lg:grid-cols-3">
                      <div className="min-w-0 rounded-2xl border border-slate-200 bg-white/90 p-3">
                        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                          Răspuns user
                        </p>
                        <p className="mt-2 break-words text-sm leading-6 text-slate-700">
                          {String(answer.selected_answer)}
                        </p>
                      </div>

                      <div className="min-w-0 rounded-2xl border border-slate-200 bg-white/90 p-3">
                        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                          Răspuns AI
                        </p>
                        <p className="mt-2 break-words text-sm leading-6 text-slate-700">
                          {aiAnswer ? String(aiAnswer.selected_answer) : '-'}
                        </p>
                      </div>

                      <div className="min-w-0 rounded-2xl border border-slate-200 bg-white/90 p-3">
                        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                          Răspuns corect
                        </p>
                        <p className="mt-2 break-words text-sm leading-6 text-slate-700">
                          {String(answer.question.correct_answer)}
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 flex flex-wrap gap-3">
                      <p
                        className={`text-sm font-semibold ${
                          answer.is_correct ? 'text-emerald-700' : 'text-rose-700'
                        }`}
                      >
                        User: {answer.is_correct ? 'Corect' : 'Greșit'}
                      </p>

                      {aiAnswer && (
                        <p
                          className={`text-sm font-semibold ${
                            aiAnswer.is_correct ? 'text-emerald-700' : 'text-rose-700'
                          }`}
                        >
                          AI: {aiAnswer.is_correct ? 'Corect' : 'Greșit'}
                        </p>
                      )}
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