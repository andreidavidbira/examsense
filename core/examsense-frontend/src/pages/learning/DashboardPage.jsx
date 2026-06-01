import { useEffect, useMemo, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import api from '../../api/axios'
import EmptyState from '../../components/common/EmptyState'
import ErrorAlert from '../../components/common/ErrorAlert'
import PageLoader from '../../components/common/PageLoader'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import StatCard from '../../components/common/StatCard'
import usePageTitle from '../../hooks/usePageTitle'

const SCORE_COLORS = ['#6366f1', '#8b5cf6', '#06b6d4']
const ANSWER_COLORS = ['#10b981', '#f43f5e']

function ModeSection({ title, stats }) {
  return (
    <SectionCard title={title}>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard label="Quiz-uri" value={stats.total_attempts} />
        <StatCard label="Scor mediu user" value={stats.average_score} />
        <StatCard label="Scor maxim user" value={stats.best_score} />
        <StatCard label="Scor mediu AI" value={stats.ai_average_score} />
        <StatCard label="Scor maxim AI" value={stats.ai_best_score} />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard label="Răspunsuri corecte" value={stats.correct_answers} />
        <StatCard label="Răspunsuri greșite" value={stats.wrong_answers} />
        <StatCard label="User wins" value={stats.user_wins} />
        <StatCard label="AI wins" value={stats.ai_wins} />
        <StatCard label="Ties" value={stats.ties} />
      </div>
    </SectionCard>
  )
}

export default function DashboardPage() {
  usePageTitle('Dashboard')

  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchDashboard() {
      try {
        const response = await api.get('/learning/dashboard/')
        setData(response.data)
      } catch {
        setError('Nu am putut încărca dashboard-ul. Reîncearcă în câteva momente.')
      }
    }

    fetchDashboard()
  }, [])

  const scoreChartData = useMemo(() => {
    if (!data) return []

    return [
      { name: 'User overall', value: data.overall.average_score },
      { name: 'AI overall', value: data.overall.ai_average_score },
      { name: 'Best user', value: data.overall.best_score },
    ]
  }, [data])

  const answersChartData = useMemo(() => {
    if (!data) return []

    return [
      { name: 'Corecte', value: data.overall.correct_answers },
      { name: 'Greșite', value: data.overall.wrong_answers },
    ]
  }, [data])

  if (error) {
    return (
      <PageContainer>
        <ErrorAlert message={error} />
      </PageContainer>
    )
  }

  if (!data) {
    return (
      <PageContainer>
        <PageLoader text="Se încarcă dashboard-ul..." />
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <div className="space-y-6">
        <ModeSection title="Overall" stats={data.overall} />
        <ModeSection title="Quiz-uri generate cu NLP" stats={data.nlp} />
        <ModeSection title="Quiz-uri generate cu AI" stats={data.ai} />

        <div className="grid gap-6 xl:grid-cols-2">
          <SectionCard
            title="Comparatie scoruri"
            subtitle="Scorul mediu user vs AI și performanța maximă."
          >
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={scoreChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="name" stroke="#64748b" />
                  <YAxis allowDecimals={true} stroke="#64748b" />
                  <Tooltip />
                  <Bar dataKey="value" radius={[10, 10, 0, 0]}>
                    {scoreChartData.map((entry, index) => (
                      <Cell
                        key={`score-cell-${index}`}
                        fill={SCORE_COLORS[index % SCORE_COLORS.length]}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>

          <SectionCard
            title="Răspunsuri corecte vs greșite"
            subtitle="Imagine rapidă asupra performanței tale generale."
          >
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={answersChartData}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={70}
                    outerRadius={110}
                    paddingAngle={3}
                  >
                    {answersChartData.map((entry, index) => (
                      <Cell
                        key={`answers-cell-${index}`}
                        fill={ANSWER_COLORS[index % ANSWER_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>

        <SectionCard
          title="Concepte slabe"
          subtitle="Conceptele unde ai acumulat cele mai multe greșeli."
        >
          {data.weak_concepts.length === 0 ? (
            <EmptyState
              title="Nu există suficiente date"
              description="Mai fă quiz-uri pentru a putea identifica punctele slabe."
            />
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {data.weak_concepts.map((item, index) => (
                <div
                  key={`${item.concept}-${index}`}
                  className="rounded-2xl border border-slate-200 bg-white p-4"
                >
                  <p className="text-lg font-semibold text-slate-950">{item.concept}</p>
                  <p className="mt-2 text-sm text-slate-500">Greșit de {item.wrong_count} ori</p>
                </div>
              ))}
            </div>
          )}
        </SectionCard>

        <SectionCard
          title="Ultimele încercări"
          subtitle="Cele mai recente quiz-uri finalizate, cu comparație user vs AI."
        >
          {data.recent_attempts.length === 0 ? (
            <EmptyState
              title="Nu există încercări"
              description="După ce finalizezi quiz-uri, aici vei vedea istoricul recent."
            />
          ) : (
            <div className="grid gap-4">
              {data.recent_attempts.map((attempt) => (
                <div
                  key={attempt.attempt_id}
                  className="rounded-2xl border border-slate-200 bg-white p-4"
                >
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-sm text-slate-500">
                          Attempt #{attempt.user_attempt_number}
                        </p>
                        <span
                          className={
                            attempt.generation_mode === 'ai'
                              ? 'rounded-full bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700'
                              : 'rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700'
                          }
                        >
                          {attempt.generation_mode.toUpperCase()}
                        </span>
                      </div>

                      <p className="mt-1 text-base font-semibold text-slate-950">
                        Document #{attempt.user_document_number}
                      </p>
                    </div>

                    <div className="text-left sm:text-right">
                      <p className="text-base font-semibold text-slate-950">
                        User: {attempt.score} / {attempt.total_questions}
                      </p>
                      <p className="text-sm text-slate-500">
                        AI: {attempt.ai_score} / {attempt.total_questions}
                      </p>
                      <p className="text-sm text-slate-500">
                        {new Date(attempt.completed_at).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </SectionCard>
      </div>
    </PageContainer>
  )
}