import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import api from '../../api/axios'
import ConfirmDialog from '../../components/common/ConfirmDialog'
import EmptyState from '../../components/common/EmptyState'
import ErrorAlert from '../../components/common/ErrorAlert'
import PageLoader from '../../components/common/PageLoader'
import PageContainer from '../../components/common/PageContainer'
import QuizOptionsDialog from '../../components/common/QuizOptionsDialog'
import SectionCard from '../../components/common/SectionCard'
import { useToast } from '../../hooks/useToast'
import usePageTitle from '../../hooks/usePageTitle'
import {
  dangerButtonClass,
  primaryButtonClass,
  secondaryButtonClass,
} from '../../utils/buttonClasses'
import { getDisplayFileName } from '../../utils/fileHelpers'
import { formatDateTime } from '../../utils/dateFormat'

function modeBadgeClass(mode) {
  return mode === 'ai'
    ? 'rounded-full bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700'
    : 'rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700'
}

export default function DocumentDetailPage() {
  usePageTitle('Detalii document')

  const { id } = useParams()
  const navigate = useNavigate()
  const { showToast } = useToast()

  const [documentData, setDocumentData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false)
  const [quizOptionsOpen, setQuizOptionsOpen] = useState(false)
  const [isGeneratingQuiz, setIsGeneratingQuiz] = useState(false)

  useEffect(() => {
    async function fetchDocument() {
      try {
        const response = await api.get(`/documents/${id}/`)
        setDocumentData(response.data)
      } catch {
        setError('Nu am putut încărca documentul. Încearcă din nou.')
      } finally {
        setLoading(false)
      }
    }

    fetchDocument()
  }, [id])

  const latestQuestionSetId = documentData?.latest_question_set_id || null

  const groupedDefinitions = useMemo(() => {
    const definitions = documentData?.definitions || []

    return {
      nlp: definitions.filter((item) => item.generation_mode === 'nlp'),
      ai: definitions.filter((item) => item.generation_mode === 'ai'),
    }
  }, [documentData])

  async function handleDeleteConfirmed() {
    try {
      await api.delete(`/documents/${id}/delete/`)
      showToast('Documentul a fost șters cu succes.', 'success')
      navigate('/documents')
    } catch {
      showToast('Nu am putut șterge documentul.', 'error')
    } finally {
      setConfirmDeleteOpen(false)
    }
  }

  async function handleGenerateNewQuiz(options) {
    try {
      setIsGeneratingQuiz(true)

      const response = await api.post(`/documents/${id}/regenerate-questions/`, {
        difficulty: options.difficulty,
        max_questions: options.max_questions,
        generation_mode: options.generation_mode,
      },
    {
      timeout: 120000, // 2 minute timeout pentru generare AI
    }
  )

      showToast('A fost generat un nou set de întrebări.', 'success')
      navigate(`/quiz/${response.data.question_set_id}`)
    } catch {
      showToast('Nu am putut genera un nou quiz.', 'error')
    } finally {
      setIsGeneratingQuiz(false)
      setQuizOptionsOpen(false)
    }
  }

  if (loading) {
    return (
      <PageContainer>
        <PageLoader text="Se încarcă documentul..." />
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

  if (!documentData) {
    return (
      <PageContainer>
        <EmptyState
          title="Document inexistent"
          description="Documentul nu a putut fi găsit."
        />
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <ConfirmDialog
        open={confirmDeleteOpen}
        title="Ștergere document"
        description="Documentul, definițiile și întrebările asociate vor fi eliminate. Acțiunea nu poate fi anulată."
        confirmText="Șterge"
        cancelText="Păstrează"
        onConfirm={handleDeleteConfirmed}
        onCancel={() => setConfirmDeleteOpen(false)}
        variant="danger"
      />

      <QuizOptionsDialog
        open={quizOptionsOpen}
        title="Generează alt quiz"
        description="Alege metoda, dificultatea și numărul de întrebări pentru noul quiz."
        confirmText="Generează"
        cancelText="Anulează"
        initialDifficulty="medium"
        initialMaxQuestions={10}
        initialGenerationMode="nlp"
        isSubmitting={isGeneratingQuiz}
        onConfirm={handleGenerateNewQuiz}
        onCancel={() => setQuizOptionsOpen(false)}
      />

      <div className="space-y-6">
        <SectionCard
          title={`Document #${documentData.user_document_number}`}
          subtitle={getDisplayFileName(documentData.file)}
          rightSlot={
            <div className="flex flex-wrap gap-3">
              {latestQuestionSetId && (
                <Link
                  to={`/quiz/${latestQuestionSetId}`}
                  className={secondaryButtonClass}
                >
                  Reia ultimul quiz
                </Link>
              )}

              <button
                onClick={() => setQuizOptionsOpen(true)}
                className={primaryButtonClass}
              >
                Quiz nou
              </button>

              <button
                onClick={() => setConfirmDeleteOpen(true)}
                className={dangerButtonClass}
              >
                Șterge documentul
              </button>
            </div>
          }
        >
          <div className="grid gap-4 sm:grid-cols-4">
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Definiții totale</p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">
                {documentData.definitions.length}
              </p>
            </div>

            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Întrebări totale</p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">
                {documentData.generated_questions.length}
              </p>
            </div>

            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Seturi quiz</p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">
                {documentData.question_sets.length}
              </p>
            </div>

            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Upload</p>
              <p className="mt-2 text-sm font-medium text-slate-900">
                {formatDateTime(documentData.uploaded_at)}
              </p>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="Seturi de quiz"
          subtitle="Fiecare set este generat separat, cu NLP sau AI."
        >
          {documentData.question_sets.length === 0 ? (
            <EmptyState
              title="Nu există seturi de quiz"
              description="Generează un quiz pentru a vedea aici seturile disponibile."
            />
          ) : (
            <div className="grid gap-4">
              {documentData.question_sets.map((item) => (
                <div
                  key={item.id}
                  className="rounded-2xl border border-slate-200 bg-white p-4"
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className={modeBadgeClass(item.generation_mode)}>
                        {item.generation_mode.toUpperCase()}
                      </span>
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                        {item.difficulty}
                      </span>
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                        {item.questions_count} întrebări
                      </span>
                    </div>

                    <Link to={`/quiz/${item.id}`} className={secondaryButtonClass}>
                      Deschide quiz
                    </Link>
                  </div>

                  <p className="mt-3 text-sm text-slate-500">
                    Generat la {formatDateTime(item.created_at)}
                  </p>
                </div>
              ))}
            </div>
          )}
        </SectionCard>

        <SectionCard
          title="Definiții extrase"
          subtitle="Conceptele identificate în document, grupate după sursă."
        >
          {documentData.definitions.length === 0 ? (
            <EmptyState
              title="Nu există definiții"
              description="Documentul nu conține definiții extrase momentan."
            />
          ) : (
            <div className="space-y-6">
              <div>
                <div className="mb-3 flex items-center gap-2">
                  <span className={modeBadgeClass('nlp')}>NLP</span>
                  <p className="text-sm text-slate-500">
                    {groupedDefinitions.nlp.length} definiții
                  </p>
                </div>

                {groupedDefinitions.nlp.length === 0 ? (
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500">
                    Nu există definiții generate cu NLP.
                  </div>
                ) : (
                  <div className="grid gap-4">
                    {groupedDefinitions.nlp.map((item) => (
                      <div
                        key={item.id}
                        className="rounded-2xl border border-slate-200 bg-white p-4"
                      >
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
                            {item.language.toUpperCase()}
                          </span>
                          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                            {item.pattern}
                          </span>
                        </div>

                        <h3 className="mt-3 text-lg font-semibold text-slate-950">
                          {item.concept}
                        </h3>
                        <p className="mt-2 text-sm leading-7 text-slate-600">
                          {item.definition}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <div className="mb-3 flex items-center gap-2">
                  <span className={modeBadgeClass('ai')}>AI</span>
                  <p className="text-sm text-slate-500">
                    {groupedDefinitions.ai.length} definiții
                  </p>
                </div>

                {groupedDefinitions.ai.length === 0 ? (
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500">
                    Nu există definiții generate cu AI.
                  </div>
                ) : (
                  <div className="grid gap-4">
                    {groupedDefinitions.ai.map((item) => (
                      <div
                        key={item.id}
                        className="rounded-2xl border border-slate-200 bg-white p-4"
                      >
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="rounded-full bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700">
                            {item.language.toUpperCase()}
                          </span>
                          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                            {item.pattern}
                          </span>
                        </div>

                        <h3 className="mt-3 text-lg font-semibold text-slate-950">
                          {item.concept}
                        </h3>
                        <p className="mt-2 text-sm leading-7 text-slate-600">
                          {item.definition}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </SectionCard>

        <SectionCard
          title="Întrebări generate"
          subtitle="Preview pentru toate întrebările salvate pentru document."
        >
          {documentData.generated_questions.length === 0 ? (
            <EmptyState
              title="Nu există întrebări"
              description="Documentul nu are încă întrebări generate."
            />
          ) : (
            <div className="grid gap-4">
              {documentData.generated_questions.map((question) => (
                <div
                  key={question.id}
                  className="rounded-2xl border border-slate-200 bg-white p-4"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={modeBadgeClass(question.generation_mode)}>
                      {question.generation_mode.toUpperCase()}
                    </span>
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      {question.question_type}
                    </span>
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      Set #{question.question_set_id}
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
      </div>
    </PageContainer>
  )
}