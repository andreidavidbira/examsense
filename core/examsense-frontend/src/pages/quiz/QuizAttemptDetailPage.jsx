import { useEffect, useState } from 'react'
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
    // incarcam toate detaliile pentru attemptul selectat
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

  // reluam exact quiz-ul deja generat pentru documentul acestui attempt
  function handleReplaySameQuiz() {
    if (!data) return
    navigate(`/documents/${data.document}/quiz`)
  }

  // generam un nou set de intrebari pentru documentul asociat attemptului
  async function handleGenerateNewQuiz(options) {
    if (!data) return

    try {
      setIsGenerating(true)

      await api.post(`/documents/${data.document}/regenerate-questions/`, {
        difficulty: options.difficulty,
        max_questions: options.max_questions,
      })

      showToast('A fost generat un nou set de întrebări.', 'success')
      navigate(`/documents/${data.document}/quiz`)
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
        description="Alege dificultatea și numărul de întrebări pentru noul quiz."
        confirmText="Generează"
        cancelText="Anulează"
        initialDifficulty="medium"
        initialMaxQuestions={10}
        isSubmitting={isGenerating}
        onConfirm={handleGenerateNewQuiz}
        onCancel={() => setQuizOptionsOpen(false)}
      />

      <div className="space-y-6">
        <SectionCard
          title={`Attempt #${data.user_attempt_number}`}
          subtitle={`Scor: ${data.score} / ${data.total_questions}`}
          rightSlot={
            <div className="flex flex-wrap gap-3">
              <button onClick={handleReplaySameQuiz} className={secondaryButtonClass}>
                Reia același quiz
              </button>
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
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Document</p>
              <p className="mt-2 text-lg font-semibold text-slate-950">
                #{data.user_document_number}
              </p>
            </div>

            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Finalizat la</p>
              <p className="mt-2 text-sm font-medium text-slate-900">
                {new Date(data.completed_at).toLocaleString()}
              </p>
            </div>
          </div>
        </SectionCard>

        <SectionCard title="Răspunsuri" subtitle="Revizuirea completă a încercării.">
          {data.answers.length === 0 ? (
            <EmptyState
              title="Nu există răspunsuri"
              description="Această încercare nu conține răspunsuri salvate."
            />
          ) : (
            <div className="grid gap-4">
              {data.answers.map((answer) => (
                <div
                  key={answer.id}
                  className={`rounded-2xl border p-4 ${
                    answer.is_correct
                      ? 'border-emerald-200 bg-emerald-50/70'
                      : 'border-rose-200 bg-rose-50/70'
                  }`}
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      {answer.question.question_type}
                    </span>
                    <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
                      {answer.question.language.toUpperCase()}
                    </span>
                  </div>

                  <p className="mt-3 text-sm font-medium text-slate-900">
                    {answer.question.question_text}
                  </p>

                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    <div className="rounded-xl bg-white/80 p-3">
                      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                        Răspuns selectat
                      </p>
                      <p className="mt-2 text-sm text-slate-700">
                        {String(answer.selected_answer)}
                      </p>
                    </div>

                    <div className="rounded-xl bg-white/80 p-3">
                      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                        Răspuns corect
                      </p>
                      <p className="mt-2 text-sm text-slate-700">
                        {String(answer.question.correct_answer)}
                      </p>
                    </div>
                  </div>

                  <p
                    className={`mt-4 text-sm font-semibold ${
                      answer.is_correct ? 'text-emerald-700' : 'text-rose-700'
                    }`}
                  >
                    {answer.is_correct ? 'Corect' : 'Greșit'}
                  </p>
                </div>
              ))}
            </div>
          )}
        </SectionCard>
      </div>
    </PageContainer>
  )
}