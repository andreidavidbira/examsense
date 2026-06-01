import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

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

function compareResultMap(aiResults = []) {
  const map = {}

  aiResults.forEach((item) => {
    map[item.question_id] = item
  })

  return map
}

function modeBadgeClass(mode) {
  return mode === 'ai'
    ? 'rounded-full bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700'
    : 'rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700'
}

export default function QuizResultPage() {
  usePageTitle('Rezultatul quiz-ului')

  const location = useLocation()
  const navigate = useNavigate()
  const { showToast } = useToast()

  const result = location.state

  const [quizOptionsOpen, setQuizOptionsOpen] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  if (!result) {
    return (
      <PageContainer>
        <EmptyState
          title="Nu există rezultat disponibil"
          description="Rezultatul quiz-ului nu este disponibil în sesiunea curentă."
        />
      </PageContainer>
    )
  }

  const aiResultsMap = compareResultMap(result.ai_results || [])

  function handleReplaySameQuiz() {
    navigate(`/quiz/${result.question_set_id}`)
  }

  async function handleGenerateNewQuiz(options) {
    setIsGenerating(true)

    try {
      const response = await api.post(`/documents/${result.document_id}/regenerate-questions/`, {
        difficulty: options.difficulty,
        max_questions: options.max_questions,
        generation_mode: options.generation_mode,
      }, {
        timeout: 120000, // 2 minute timeout pentru generare AI
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
        initialGenerationMode={result.generation_mode || 'nlp'}
        isSubmitting={isGenerating}
        onConfirm={handleGenerateNewQuiz}
        onCancel={() => setQuizOptionsOpen(false)}
      />

      <div className="space-y-6">
        <SectionCard
          title="Rezultatul quiz-ului"
          subtitle={`Scor final user: ${result.score} / ${result.total_questions}`}
          rightSlot={
            <div className="flex flex-wrap gap-3">
              <button onClick={handleReplaySameQuiz} className={secondaryButtonClass}>
                Reia același quiz
              </button>
              <button
                onClick={() => setQuizOptionsOpen(true)}
                className={secondaryButtonClass}
              >
                Generează alt quiz
              </button>
              <Link to="/quiz-history" className={secondaryButtonClass}>
                Vezi istoricul
              </Link>
              <Link
                to={`/documents/${result.document_id}`}
                className={primaryButtonClass}
              >
                Înapoi la document
              </Link>
            </div>
          }
        >
          <div className="mb-4 flex flex-wrap items-center gap-2">
            <span className={modeBadgeClass(result.generation_mode)}>
              {String(result.generation_mode || 'nlp').toUpperCase()}
            </span>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
              Set #{result.question_set_id}
            </span>
          </div>

          <div className="grid gap-4 sm:grid-cols-4">
            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Attempt</p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">
                #{result.user_attempt_number}
              </p>
            </div>

            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Document</p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">
                #{result.user_document_number}
              </p>
            </div>

            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Scor user</p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">
                {result.score} / {result.total_questions}
              </p>
            </div>

            <div className="rounded-2xl bg-slate-50 p-4">
              <p className="text-sm text-slate-500">Scor AI</p>
              <p className="mt-2 text-2xl font-semibold text-slate-950">
                {result.ai_score} / {result.ai_total_questions}
              </p>
              <p className="mt-1 text-xs text-slate-500">{result.ai_model_name}</p>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="Comparatie user vs AI"
          subtitle="Vezi cum s-a descurcat AI-ul pe același quiz."
        >
          <div className="rounded-2xl border border-slate-200 bg-white p-4">
            <p className="text-sm text-slate-600">
              {result.score > result.ai_score
                ? 'Utilizatorul a obținut un scor mai bun decât AI-ul.'
                : result.score < result.ai_score
                ? 'AI-ul a obținut un scor mai bun decât utilizatorul.'
                : 'Utilizatorul și AI-ul au obținut același scor.'}
            </p>
          </div>
        </SectionCard>

        <SectionCard
          title="Răspunsuri"
          subtitle="Revizuiește răspunsurile tale, răspunsurile AI și variantele corecte."
        >
          <div className="grid gap-4">
            {result.results.map((item, index) => {
              const aiItem = aiResultsMap[item.question_id]

              return (
                <div
                  key={`${item.question_id}-${index}`}
                  className={`rounded-2xl border p-4 ${
                    item.is_correct
                      ? 'border-emerald-200 bg-emerald-50/70'
                      : 'border-rose-200 bg-rose-50/70'
                  }`}
                >
                  <p className="text-sm font-medium text-slate-900">{item.question}</p>

                  <div className="mt-4 grid gap-3 lg:grid-cols-3">
                    <div className="rounded-xl bg-white/80 p-3">
                      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                        Răspuns user
                      </p>
                      <p className="mt-2 text-sm text-slate-700">
                        {String(item.selected_answer)}
                      </p>
                    </div>

                    <div className="rounded-xl bg-white/80 p-3">
                      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                        Răspuns AI
                      </p>
                      <p className="mt-2 text-sm text-slate-700">
                        {aiItem ? String(aiItem.ai_selected_answer) : '-'}
                      </p>
                    </div>

                    <div className="rounded-xl bg-white/80 p-3">
                      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                        Răspuns corect
                      </p>
                      <p className="mt-2 text-sm text-slate-700">
                        {String(item.correct_answer)}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-4">
                    <p
                      className={`text-sm font-semibold ${
                        item.is_correct ? 'text-emerald-700' : 'text-rose-700'
                      }`}
                    >
                      User: {item.is_correct ? 'Corect' : 'Greșit'}
                    </p>

                    {aiItem && (
                      <p
                        className={`text-sm font-semibold ${
                          aiItem.is_correct ? 'text-emerald-700' : 'text-rose-700'
                        }`}
                      >
                        AI: {aiItem.is_correct ? 'Corect' : 'Greșit'}
                      </p>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </SectionCard>
      </div>
    </PageContainer>
  )
}