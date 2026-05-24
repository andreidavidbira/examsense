import { useEffect, useMemo, useState } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import api from '../../api/axios'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import StatCard from '../../components/common/StatCard'
import EmptyState from '../../components/common/EmptyState'
import ErrorAlert from '../../components/common/ErrorAlert'
import PageLoader from '../../components/common/PageLoader'

const SCORE_COLORS = ['#6366f1', '#8b5cf6', '#06b6d4']
const ANSWER_COLORS = ['#10b981', '#f43f5e']

export default function DashboardPage() {
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
      { name: 'Scor mediu', value: data.average_score },
      { name: 'Scor maxim', value: data.best_score },
      { name: 'Scor minim', value: data.worst_score },
    ]
  }, [data])

  const answersChartData = useMemo(() => {
    if (!data) return []
    return [
      { name: 'Corecte', value: data.correct_answers },
      { name: 'Greșite', value: data.wrong_answers },
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
        <SectionCard
          title="Dashboard"
          subtitle="Privire de ansamblu asupra progresului tău în ExamSense+."
        >
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="Quiz-uri totale" value={data.total_attempts} />
            <StatCard label="Scor mediu" value={data.average_score} />
            <StatCard label="Scor maxim" value={data.best_score} />
            <StatCard label="Scor minim" value={data.worst_score} />
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <StatCard label="Răspunsuri corecte" value={data.correct_answers} />
            <StatCard label="Răspunsuri greșite" value={data.wrong_answers} />
          </div>
        </SectionCard>

        <div className="grid gap-6 xl:grid-cols-2">
          <SectionCard
            title="Distribuția scorurilor"
            subtitle="Comparație rapidă între scorul mediu, minim și maxim."
          >
            <div className="h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={scoreChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="name" stroke="#64748b" />
                  <YAxis allowDecimals={true} stroke="#64748b" />
                  <Tooltip />
                  <Bar dataKey="value" radius={[10, 10, 0, 0]}>
                    {scoreChartData.map((entry, index) => (
                      <Cell key={`score-cell-${index}`} fill={SCORE_COLORS[index % SCORE_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>

          <SectionCard
            title="Răspunsuri corecte vs greșite"
            subtitle="Imagine rapidă asupra calității răspunsurilor tale."
          >
            <div className="h-[320px]">
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
                      <Cell key={`answers-cell-${index}`} fill={ANSWER_COLORS[index % ANSWER_COLORS.length]} />
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
                  <p className="mt-2 text-sm text-slate-500">
                    Greșit de {item.wrong_count} ori
                  </p>
                </div>
              ))}
            </div>
          )}
        </SectionCard>

        <SectionCard
          title="Ultimele încercări"
          subtitle="Cele mai recente quiz-uri finalizate."
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
                      <p className="text-sm text-slate-500">
                        Attempt #{attempt.user_attempt_number}
                      </p>
                      <p className="mt-1 text-base font-semibold text-slate-950">
                        Document #{attempt.user_document_number}
                      </p>
                    </div>

                    <div className="text-left sm:text-right">
                      <p className="text-base font-semibold text-slate-950">
                        {attempt.score} / {attempt.total_questions}
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