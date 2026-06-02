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
import { formatDateTime } from '../../utils/dateFormat'

const SCORE_COLORS = ['#6366f1', '#8b5cf6', '#06b6d4']
const ANSWER_COLORS = ['#10b981', '#f43f5e']
const DUEL_COLORS = ['#0f172a', '#8b5cf6', '#f59e0b']
const MODE_COMPARE_COLORS = ['#0f172a', '#8b5cf6']

function ModeSection({ title, stats, accent }) {
  return (
    <SectionCard title={title} className="min-w-0">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard label="Quiz-uri" value={stats.total_attempts} accent={accent} />
        <StatCard label="Scor mediu user" value={stats.average_score} accent={accent} />
        <StatCard label="Scor maxim user" value={stats.best_score} accent={accent} />
        <StatCard label="Scor mediu AI" value={stats.ai_average_score} accent={accent} />
        <StatCard label="Scor maxim AI" value={stats.ai_best_score} accent={accent} />
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <StatCard label="Răspunsuri corecte" value={stats.correct_answers} accent="emerald" />
        <StatCard label="Răspunsuri greșite" value={stats.wrong_answers} accent="rose" />
        <StatCard label="User wins" value={stats.user_wins} accent="brand" />
        <StatCard label="AI wins" value={stats.ai_wins} accent="violet" />
        <StatCard label="Ties" value={stats.ties} accent="amber" />
      </div>
    </SectionCard>
  )
}

function DuelSummaryCard({ overall }) {
  const totalDuels = (overall?.user_wins || 0) + (overall?.ai_wins || 0) + (overall?.ties || 0)
  const userLead = (overall?.average_score || 0) - (overall?.ai_average_score || 0)

  let leaderText = 'User și AI sunt la egalitate.'
  if (userLead > 0) {
    leaderText = 'Userul are avantaj la scorul mediu.'
  } else if (userLead < 0) {
    leaderText = 'AI-ul are avantaj la scorul mediu.'
  }

  return (
    <SectionCard
      title="Duel User vs AI"
      subtitle="O vedere rapidă asupra competiției dintre performanța utilizatorului și solverul AI."
      className="min-w-0"
    >
      <div className="grid gap-4 lg:grid-cols-[1fr_1fr]">
        <div className="rounded-[26px] border border-brand-200 bg-brand-50/70 p-5">
          <p className="text-sm font-medium text-brand-700">Rezumat duel</p>
          <p className="mt-3 text-2xl font-semibold tracking-tight text-slate-950">
            {leaderText}
          </p>
          <p className="mt-3 text-sm leading-7 text-slate-600">
            User wins: {overall?.user_wins || 0} · AI wins: {overall?.ai_wins || 0} · Ties: {overall?.ties || 0}
          </p>
          <p className="mt-2 text-sm text-slate-600">
            Total dueluri evaluate: {totalDuels}
          </p>
        </div>

        <div className="rounded-[26px] border border-violet-200 bg-violet-50/70 p-5">
          <p className="text-sm font-medium text-violet-700">Diferență scor mediu</p>
          <p className="mt-3 text-4xl font-semibold tracking-tight text-slate-950">
            {userLead > 0 ? '+' : ''}
            {Number(userLead || 0).toFixed(2)}
          </p>
          <p className="mt-3 text-sm leading-7 text-slate-600">
            Valoarea reprezintă scorul mediu User minus scorul mediu AI, calculat pe quiz-urile finalizate.
          </p>
        </div>
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

  const duelChartData = useMemo(() => {
    if (!data) return []

    return [
      { name: 'User wins', value: data.overall.user_wins },
      { name: 'AI wins', value: data.overall.ai_wins },
      { name: 'Ties', value: data.overall.ties },
    ]
  }, [data])

  const modeCompareData = useMemo(() => {
    if (!data) return []

    return [
      {
        name: 'Overall',
        user: data.overall.average_score,
        ai: data.overall.ai_average_score,
      },
      {
        name: 'NLP',
        user: data.nlp.average_score,
        ai: data.nlp.ai_average_score,
      },
      {
        name: 'AI',
        user: data.ai.average_score,
        ai: data.ai.ai_average_score,
      },
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
        <div className="rounded-[30px] border border-brand-100 bg-linear-to-r from-brand-50 via-violet-50 to-white p-6 shadow-sm">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">
            Dashboard
          </h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            Vezi separat performanța pe quiz-uri generate cu NLP și AI, plus comparația directă dintre User și solverul AI.
          </p>
        </div>

        <DuelSummaryCard overall={data.overall} />

        <ModeSection title="Overall" stats={data.overall} accent="brand" />
        <ModeSection title="Quiz-uri generate cu NLP" stats={data.nlp} accent="emerald" />
        <ModeSection title="Quiz-uri generate cu AI" stats={data.ai} accent="violet" />

        <div className="grid min-w-0 gap-6 xl:grid-cols-2">
          <SectionCard
            title="Comparatie scoruri"
            subtitle="Scorul mediu user vs AI și performanța maximă."
            className="min-w-0"
          >
            {scoreChartData.length > 0 && (
              <div className="w-full min-w-0 overflow-hidden rounded-2xl">
                <div className="h-72 w-full min-w-0 sm:h-80">
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
              </div>
            )}
          </SectionCard>

          <SectionCard
            title="Răspunsuri corecte vs greșite"
            subtitle="Imagine rapidă asupra performanței tale generale."
            className="min-w-0"
          >
            {answersChartData.length > 0 && (
              <div className="w-full min-w-0 overflow-hidden rounded-2xl">
                <div className="h-72 w-full min-w-0 sm:h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={answersChartData}
                        dataKey="value"
                        nameKey="name"
                        innerRadius={60}
                        outerRadius={100}
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
              </div>
            )}
          </SectionCard>
        </div>

        <div className="grid min-w-0 gap-6 xl:grid-cols-2">
          <SectionCard
            title="Distribuție dueluri"
            subtitle="Câte quiz-uri au fost câștigate de User, AI sau terminate la egalitate."
            className="min-w-0"
          >
            {duelChartData.length > 0 && (
              <div className="w-full min-w-0 overflow-hidden rounded-2xl">
                <div className="h-72 w-full min-w-0 sm:h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={duelChartData}
                        dataKey="value"
                        nameKey="name"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={3}
                      >
                        {duelChartData.map((entry, index) => (
                          <Cell
                            key={`duel-cell-${index}`}
                            fill={DUEL_COLORS[index % DUEL_COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </SectionCard>

          <SectionCard
            title="User vs AI pe moduri"
            subtitle="Compară scorul mediu al Userului cu scorul mediu al AI-ului pe Overall, NLP și AI."
            className="min-w-0"
          >
            {modeCompareData.length > 0 && (
              <div className="w-full min-w-0 overflow-hidden rounded-2xl">
                <div className="h-72 w-full min-w-0 sm:h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={modeCompareData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="name" stroke="#64748b" />
                      <YAxis allowDecimals={true} stroke="#64748b" />
                      <Tooltip />
                      <Bar dataKey="user" radius={[8, 8, 0, 0]}>
                        {modeCompareData.map((_, index) => (
                          <Cell
                            key={`mode-user-${index}`}
                            fill={MODE_COMPARE_COLORS[0]}
                          />
                        ))}
                      </Bar>
                      <Bar dataKey="ai" radius={[8, 8, 0, 0]}>
                        {modeCompareData.map((_, index) => (
                          <Cell
                            key={`mode-ai-${index}`}
                            fill={MODE_COMPARE_COLORS[1]}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </SectionCard>
        </div>

        <SectionCard
          title="Concepte slabe"
          subtitle="Conceptele unde ai acumulat cele mai multe greșeli."
          className="min-w-0"
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
                  className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
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
          className="min-w-0"
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
                  className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div className="min-w-0">
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
                        {formatDateTime(attempt.completed_at)}
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