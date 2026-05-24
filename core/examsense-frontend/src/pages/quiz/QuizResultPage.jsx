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

export default function QuizResultPage() {
  usePageTitle('Rezultatul quiz-ului')

  const location = useLocation()
  const navigate = useNavigate()
  const { showToast } = useToast()

  const result = location.state

  const [quizOptionsOpen, setQuizOptionsOpen] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  // daca utilizatorul intra direct pe pagina fara state, afisam empty state
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

  // reluam exact acelasi quiz deja generat pentru document
  function handleReplaySameQuiz() {
    navigate(`/documents/${result.document_id}/quiz`)
  }

  // generam un nou set de intrebari si redirectionam utilizatorul catre noul quiz
  async function handleGenerateNewQuiz(options) {
    setIsGenerating(true)

    try {
      await api.post(`/documents/${result.document_id}/regenerate-questions/`, {
        difficulty: options.difficulty,
        max_questions: options.max_questions,
      })

      showToast('A fost generat un nou set de întrebări.', 'success')
      navigate(`/documents/${result.document_id}/quiz`)
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
          title="Rezultatul quiz-ului"
          subtitle={`Scor final: ${result.score} / ${result.total_questions}`}
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
          <div className="grid gap-4 sm:grid-cols-2">
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
          </div>
        </SectionCard>

        <SectionCard
          title="Răspunsuri"
          subtitle="Revizuiește răspunsurile tale și compară-le cu cele corecte."
        >
          <div className="grid gap-4">
            {result.results.map((item, index) => (
              <div
                key={`${item.question_id}-${index}`}
                className={`rounded-2xl border p-4 ${
                  item.is_correct
                    ? 'border-emerald-200 bg-emerald-50/70'
                    : 'border-rose-200 bg-rose-50/70'
                }`}
              >
                <p className="text-sm font-medium text-slate-900">{item.question}</p>

                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-xl bg-white/80 p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                      Răspuns selectat
                    </p>
                    <p className="mt-2 text-sm text-slate-700">
                      {String(item.selected_answer)}
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

                <p
                  className={`mt-4 text-sm font-semibold ${
                    item.is_correct ? 'text-emerald-700' : 'text-rose-700'
                  }`}
                >
                  {item.is_correct ? 'Corect' : 'Greșit'}
                </p>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>
    </PageContainer>
  )
}