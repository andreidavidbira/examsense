import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import api from '../../api/axios'
import EmptyState from '../../components/common/EmptyState'
import ErrorAlert from '../../components/common/ErrorAlert'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import usePageTitle from '../../hooks/usePageTitle'
import {
  primaryButtonClass,
  secondaryButtonClass,
} from '../../utils/buttonClasses'

function modeBadgeClass(mode) {
  return mode === 'ai'
    ? 'rounded-full bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700'
    : 'rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700'
}

export default function QuizPlayPage() {
  usePageTitle('Quiz')

  const { questionSetId } = useParams()
  const navigate = useNavigate()

  const [quizData, setQuizData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    async function fetchQuestionSet() {
      try {
        const response = await api.get(`/documents/question-sets/${questionSetId}/quiz/`)
        setQuizData(response.data)
      } catch {
        setError('Nu am putut încărca quiz-ul pentru acest set de întrebări.')
      } finally {
        setLoading(false)
      }
    }

    fetchQuestionSet()
  }, [questionSetId])

  const questions = useMemo(() => {
    return quizData?.questions || []
  }, [quizData])

  const currentQuestion = questions[currentIndex]
  const answeredCount = questions.filter((question) => answers[question.id] !== undefined).length
  const allAnswered = questions.length > 0 && answeredCount === questions.length

  function setAnswer(questionId, value) {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: value,
    }))
  }

  function goNext() {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  function goPrev() {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  async function handleSubmitQuiz() {
    if (!quizData || !allAnswered) {
      return
    }

    setIsSubmitting(true)

    try {
      const payload = {
        question_set_id: Number(questionSetId),
        answers: questions.map((question) => ({
          question_id: question.id,
          selected_answer: answers[question.id],
        })),
      }

      const response = await api.post('/documents/submit-quiz/', payload, {
        timeout: 120000, // 2 minute timeout pentru generare AI
      })

      navigate('/quiz-result', {
        state: response.data,
      })
    } catch {
      setError('Trimiterea quiz-ului a eșuat.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (loading) {
    return (
      <PageContainer>
        <p className="text-sm text-slate-500">Se încarcă quiz-ul...</p>
      </PageContainer>
    )
  }

  if (error) {
    return (
      <PageContainer>
        <ErrorAlert message={error} />
      </PageContainer>
    )
  }

  if (!questions.length) {
    return (
      <PageContainer>
        <EmptyState
          title="Nu există întrebări"
          description="Setul de quiz nu conține încă întrebări."
        />
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <div className="space-y-5 pb-28 sm:space-y-6 sm:pb-0">
        <SectionCard
          title={`Quiz document #${quizData.user_document_number}`}
          subtitle={`Set #${quizData.question_set_id}`}
        >
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap items-center gap-2">
              <span className={modeBadgeClass(quizData.generation_mode)}>
                {quizData.generation_mode.toUpperCase()}
              </span>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                {quizData.difficulty}
              </span>
            </div>

            <p className="text-sm font-medium text-slate-700">
              Răspunse: {answeredCount} / {questions.length}
            </p>
          </div>

          <div className="mb-4">
            <p className="text-sm text-slate-500">
              Întrebarea {currentIndex + 1} din {questions.length}
            </p>
          </div>

          <div className="mb-5 h-2 w-full overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-linear-to-r from-brand-500 to-violet-500 transition-all"
              style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
            />
          </div>

          <div className="mb-5 grid grid-cols-5 gap-2 sm:grid-cols-10">
            {questions.map((question, index) => {
              const isActive = index === currentIndex
              const isAnswered = answers[question.id] !== undefined

              return (
                <button
                  key={question.id}
                  onClick={() => {
                    setCurrentIndex(index)
                    window.scrollTo({ top: 0, behavior: 'smooth' })
                  }}
                  className={`rounded-xl px-3 py-2 text-sm font-medium transition ${
                    isActive
                      ? 'bg-slate-950 text-white'
                      : isAnswered
                      ? 'border border-brand-200 bg-brand-50 text-brand-700'
                      : 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  {index + 1}
                </button>
              )
            })}
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5">
            <div className="flex flex-wrap items-center gap-2">
              <span className={modeBadgeClass(quizData.generation_mode)}>
                {quizData.generation_mode.toUpperCase()}
              </span>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                {currentQuestion.question_type}
              </span>
              <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
                {currentQuestion.language.toUpperCase()}
              </span>
            </div>

            <h3 className="mt-4 text-xl font-semibold tracking-tight text-slate-950">
              {currentQuestion.question_text}
            </h3>

            <div className="mt-6">
              {currentQuestion.question_type === 'true_false' ? (
                <div className="grid gap-3 sm:grid-cols-2">
                  {[true, false].map((value) => {
                    const isSelected = answers[currentQuestion.id] === value

                    return (
                      <button
                        key={String(value)}
                        onClick={() => setAnswer(currentQuestion.id, value)}
                        className={`rounded-2xl border px-4 py-3 text-left text-sm font-medium transition ${
                          isSelected
                            ? 'border-brand-500 bg-brand-50 text-brand-700'
                            : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                        }`}
                      >
                        {value ? 'Adevărat / True' : 'Fals / False'}
                      </button>
                    )
                  })}
                </div>
              ) : (
                <div className="grid gap-3">
                  {(currentQuestion.options || []).map((option, index) => {
                    const isSelected = answers[currentQuestion.id] === option

                    return (
                      <button
                        key={`${currentQuestion.id}-option-${index}`}
                        onClick={() => setAnswer(currentQuestion.id, option)}
                        className={`rounded-2xl border px-4 py-3 text-left text-sm leading-6 transition ${
                          isSelected
                            ? 'border-brand-500 bg-brand-50 text-brand-700'
                            : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                        }`}
                      >
                        {option}
                      </button>
                    )
                  })}
                </div>
              )}
            </div>
          </div>

          {!allAnswered && (
            <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
              Trebuie să răspunzi la toate întrebările înainte să poți trimite quiz-ul.
            </div>
          )}

          <div className="mt-6 hidden flex-col gap-3 sm:flex sm:flex-row sm:justify-between">
            <button
              onClick={goPrev}
              disabled={currentIndex === 0}
              className={`${secondaryButtonClass} disabled:opacity-50`}
            >
              Înapoi
            </button>

            <div className="flex flex-col gap-3 sm:flex-row">
              {currentIndex < questions.length - 1 ? (
                <button onClick={goNext} className={primaryButtonClass}>
                  Următoarea întrebare
                </button>
              ) : (
                <button
                  onClick={handleSubmitQuiz}
                  disabled={isSubmitting || !allAnswered}
                  className={primaryButtonClass}
                >
                  {isSubmitting ? 'Se trimite...' : 'Trimite quiz-ul'}
                </button>
              )}
            </div>
          </div>
        </SectionCard>
      </div>

      <div className="fixed inset-x-0 bottom-0 z-40 border-t border-slate-200 bg-white/95 p-3 backdrop-blur sm:hidden">
        <div className="mx-auto flex max-w-3xl gap-3">
          <button
            onClick={goPrev}
            disabled={currentIndex === 0}
            className={`flex-1 ${secondaryButtonClass} disabled:opacity-50`}
          >
            Înapoi
          </button>

          {currentIndex < questions.length - 1 ? (
            <button onClick={goNext} className={`flex-1 ${primaryButtonClass}`}>
              Următoarea
            </button>
          ) : (
            <button
              onClick={handleSubmitQuiz}
              disabled={isSubmitting || !allAnswered}
              className={`flex-1 ${primaryButtonClass}`}
            >
              {isSubmitting ? 'Se trimite...' : 'Trimite'}
            </button>
          )}
        </div>
      </div>
    </PageContainer>
  )
}