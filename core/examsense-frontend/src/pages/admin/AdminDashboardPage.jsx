/*
ExamSense+ - Admin Dashboard Page
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste pagina principala a panoului de administrare
- afiseaza statistici globale despre utilizatori, documente, question set-uri si attempt-uri
- include grafice pentru raspunsuri, scoruri si comparatia dintre useri si AI
- permite actiuni administrative precum activarea utilizatorilor si stergerea documentelor
*/

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
import ConfirmDialog from '../../components/common/ConfirmDialog'
import ErrorAlert from '../../components/common/ErrorAlert'
import PageLoader from '../../components/common/PageLoader'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import StatCard from '../../components/common/StatCard'
import { useToast } from '../../hooks/useToast'
import usePageTitle from '../../hooks/usePageTitle'
import {
  dangerButtonClass,
  primaryButtonClass,
  secondaryButtonClass,
} from '../../utils/buttonClasses'
import { getDisplayFileName } from '../../utils/fileHelpers'
import { formatDuration } from '../../utils/timeFormat'
import { formatDateTime } from '../../utils/dateFormat'
import Pagination from '../../components/common/Pagination'

const PAGE_SIZE = 5
const ANSWER_COLORS = ['#10b981', '#f43f5e']
const COMPARE_COLORS = ['#0f172a', '#8b5cf6']
const MODE_COLORS = ['#10b981', '#8b5cf6']
const USER_DUEL_COLORS = ['#0f172a', '#8b5cf6', '#f59e0b']

// micsoram usor butoanele pentru zonele dense din admin
function compactButtonClass(baseClass) {
  return `${baseClass} min-h-0 px-3 py-2 text-xs sm:text-sm`
}


// extragem elementele pentru pagina curenta
function paginate(items, page) {
  const start = (page - 1) * PAGE_SIZE
  return items.slice(start, start + PAGE_SIZE)
}

// calculam numarul total de pagini pentru o colectie
function totalPages(items) {
  return Math.max(1, Math.ceil(items.length / PAGE_SIZE))
}

// afisam un grup de statistici pentru un mod anume
function ModeStatsGrid({ title, stats }) {
  if (!stats) return null

  return (
    <SectionCard title={title}>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
        <StatCard label="Attempts" value={stats.attempts_count} accent="brand" />
        <StatCard label="Corecte" value={stats.correct_answers} accent="emerald" />
        <StatCard label="Greșite" value={stats.wrong_answers} accent="rose" />
        <StatCard label="Scor mediu" value={stats.average_score} accent="brand" />
        <StatCard label="Scor maxim" value={stats.best_score} accent="violet" />
        <StatCard label="Scor minim" value={stats.worst_score} accent="amber" />
      </div>
    </SectionCard>
  )
}

// wrapper reutilizabil pentru cardurile cu grafice
function ChartCard({ title, subtitle, children }) {
  return (
    <SectionCard title={title} subtitle={subtitle} className="min-w-0">
      <div className="w-full min-w-0 overflow-hidden rounded-2xl">
        <div className="h-72 w-full min-w-0 sm:h-80">
          {children}
        </div>
      </div>
    </SectionCard>
  )
}

// afisam dashboard-ul principal pentru administrarea platformei
export default function AdminDashboardPage() {
  usePageTitle('Panoul de administrare')
  const { showToast } = useToast()

  const [overview, setOverview] = useState(null)
  const [aiOverview, setAiOverview] = useState(null)
  const [users, setUsers] = useState([])
  const [documents, setDocuments] = useState([])
  const [attempts, setAttempts] = useState([])
  const [questionSets, setQuestionSets] = useState([])
  const [selectedUserDetail, setSelectedUserDetail] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [selectedUser, setSelectedUser] = useState(null)
  const [selectedDocument, setSelectedDocument] = useState(null)
  const [selectedUserId, setSelectedUserId] = useState(null)

  const [usersPage, setUsersPage] = useState(1)
  const [documentsPage, setDocumentsPage] = useState(1)
  const [questionSetsPage, setQuestionSetsPage] = useState(1)
  const [attemptsPage, setAttemptsPage] = useState(1)

  // incarcam toate sursele principale de date pentru admin
  async function fetchAll() {
    try {
      setLoading(true)

      const [
        overviewResponse,
        aiOverviewResponse,
        usersResponse,
        documentsResponse,
        attemptsResponse,
        questionSetsResponse,
      ] = await Promise.all([
        api.get('/adminpanel/overview/'),
        api.get('/adminpanel/ai-overview/'),
        api.get('/adminpanel/users/'),
        api.get('/adminpanel/documents/'),
        api.get('/adminpanel/attempts/'),
        api.get('/adminpanel/question-sets/'),
      ])

      setOverview(overviewResponse.data)
      setAiOverview(aiOverviewResponse.data)
      setUsers(usersResponse.data.results || [])
      setDocuments(documentsResponse.data.results || [])
      setAttempts(attemptsResponse.data.results || [])
      setQuestionSets(questionSetsResponse.data.results || [])
      setError('')
    } catch {
      setError('Nu am putut încărca panoul de administrare.')
    } finally {
      setLoading(false)
    }
  }

  // incarcam dashboard-ul detaliat pentru un utilizator selectat
  async function fetchUserDetail(userId) {
    try {
      const response = await api.get(`/adminpanel/users/${userId}/`)
      setSelectedUserDetail(response.data)
      setSelectedUserId(userId)
    } catch {
      showToast('Nu am putut încărca dashboardul utilizatorului.', 'error')
    }
  }

  useEffect(() => {
    fetchAll()
  }, [])

  // activam sau dezactivam utilizatorul selectat
  async function handleToggleUserActive() {
    if (!selectedUser) return

    try {
      const response = await api.patch(`/adminpanel/users/${selectedUser.id}/toggle-active/`, {
        is_active: !selectedUser.is_active,
      })

      const newIsActive = response.data.is_active

      setUsers((prev) =>
        prev.map((user) =>
          user.id === selectedUser.id
            ? { ...user, is_active: newIsActive }
            : user
        )
      )

      if (selectedUserDetail?.user?.id === selectedUser.id) {
        setSelectedUserDetail((prev) => ({
          ...prev,
          user: {
            ...prev.user,
            is_active: newIsActive,
          },
        }))
      }

      showToast('Starea utilizatorului a fost actualizată.', 'success')
      setSelectedUser(null)
    } catch {
      showToast('Nu am putut actualiza utilizatorul.', 'error')
    }
  }

  // stergem documentul selectat
  async function handleDeleteDocument() {
    if (!selectedDocument) return

    try {
      await api.delete(`/adminpanel/documents/${selectedDocument.id}/delete/`)

      setDocuments((prev) => prev.filter((doc) => doc.id !== selectedDocument.id))
      setSelectedDocument(null)

      showToast('Documentul a fost șters.', 'success')
    } catch {
      showToast('Nu am putut șterge documentul.', 'error')
    }
  }

  const pagedUsers = useMemo(() => paginate(users, usersPage), [users, usersPage])
  const pagedDocuments = useMemo(() => paginate(documents, documentsPage), [documents, documentsPage])
  const pagedQuestionSets = useMemo(() => paginate(questionSets, questionSetsPage), [questionSets, questionSetsPage])
  const pagedAttempts = useMemo(() => paginate(attempts, attemptsPage), [attempts, attemptsPage])

  // distributia globala a raspunsurilor corecte si gresite
  const globalAnswerDistributionData = useMemo(() => {
    if (!overview) return []

    return [
      { name: 'Corecte', value: Number(overview.correct_answers || 0) },
      { name: 'Greșite', value: Number(overview.wrong_answers || 0) },
    ]
  }, [overview])

  // comparatia globala dintre useri si AI pe moduri
  const globalScoreCompareData = useMemo(() => {
    if (!overview || !aiOverview) return []

    return [
      {
        name: 'Overall',
        user: Number(overview.average_score || 0),
        ai: Number(aiOverview.overall?.average_score || 0),
      },
      {
        name: 'NLP',
        user: Number(overview.nlp_average_score || 0),
        ai: Number(aiOverview.nlp?.average_score || 0),
      },
      {
        name: 'AI',
        user: Number(overview.ai_average_score || 0),
        ai: Number(aiOverview.ai?.average_score || 0),
      },
    ]
  }, [overview, aiOverview])

  // volumul incercarilor pentru NLP si AI
  const globalModeVolumeData = useMemo(() => {
    if (!overview) return []

    return [
      { name: 'NLP attempts', value: Number(overview.nlp_attempts || 0) },
      { name: 'AI attempts', value: Number(overview.ai_attempts || 0) },
    ]
  }, [overview])

  // distributia duelurilor pentru utilizatorul selectat
  const selectedUserDuelData = useMemo(() => {
    if (!selectedUserDetail?.user_vs_ai_overall) return []

    return [
      {
        name: 'User wins',
        value: Number(selectedUserDetail.user_vs_ai_overall.user_wins || 0),
      },
      {
        name: 'AI wins',
        value: Number(selectedUserDetail.user_vs_ai_overall.ai_wins || 0),
      },
      {
        name: 'Ties',
        value: Number(selectedUserDetail.user_vs_ai_overall.draws || 0),
      },
    ]
  }, [selectedUserDetail])

  // comparatia dintre utilizator si AI pentru utilizatorul selectat
  const selectedUserModeCompareData = useMemo(() => {
    if (!selectedUserDetail) return []

    return [
      {
        name: 'Overall',
        user: Number(selectedUserDetail.overall?.average_score || 0),
        ai: Number(selectedUserDetail.ai_solver_overall?.average_score || 0),
      },
      {
        name: 'NLP',
        user: Number(selectedUserDetail.nlp?.average_score || 0),
        ai: Number(selectedUserDetail.ai_solver_nlp?.average_score || 0),
      },
      {
        name: 'AI',
        user: Number(selectedUserDetail.ai?.average_score || 0),
        ai: Number(selectedUserDetail.ai_solver_ai?.average_score || 0),
      },
    ]
  }, [selectedUserDetail])

  if (loading) {
    return (
      <PageContainer>
        <PageLoader text="Se încarcă panoul de administrare..." />
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

  return (
    <PageContainer>
      <ConfirmDialog
        open={!!selectedUser}
        title={selectedUser?.is_active ? 'Dezactivează utilizator' : 'Activează utilizator'}
        description={
          selectedUser?.is_active
            ? `Sigur vrei să dezactivezi utilizatorul ${selectedUser?.username}?`
            : `Sigur vrei să activezi utilizatorul ${selectedUser?.username}?`
        }
        confirmText={selectedUser?.is_active ? 'Dezactivează' : 'Activează'}
        cancelText="Anulează"
        onConfirm={handleToggleUserActive}
        onCancel={() => setSelectedUser(null)}
        variant={selectedUser?.is_active ? 'danger' : 'primary'}
      />

      <ConfirmDialog
        open={!!selectedDocument}
        title="Ștergere document"
        description={`Sigur vrei să ștergi documentul ${
          selectedDocument ? getDisplayFileName(selectedDocument.file) : ''
        }?`}
        confirmText="Șterge"
        cancelText="Anulează"
        onConfirm={handleDeleteDocument}
        onCancel={() => setSelectedDocument(null)}
        variant="danger"
      />

      <div className="space-y-6">
        <div className="rounded-[30px] border border-brand-100 bg-linear-to-r from-brand-50 via-violet-50 to-white p-6 shadow-sm">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">
            Admin Control Panel
          </h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            Statistici globale, comparații NLP vs AI și accent puternic pe duelul dintre utilizatori și solverul AI.
          </p>
        </div>

        <SectionCard title="Overview global">
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <StatCard label="Utilizatori" value={overview?.total_users || 0} accent="brand" />
            <StatCard label="Utilizatori activi" value={overview?.active_users || 0} accent="emerald" />
            <StatCard label="Documente" value={overview?.total_documents || 0} accent="violet" />
            <StatCard label="Question sets" value={overview?.total_question_sets || 0} accent="amber" />
            <StatCard label="Attempts" value={overview?.total_attempts || 0} accent="brand" />
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <StatCard label="Răspunsuri totale" value={overview?.total_answers || 0} accent="brand" />
            <StatCard label="Corecte" value={overview?.correct_answers || 0} accent="emerald" />
            <StatCard label="Greșite" value={overview?.wrong_answers || 0} accent="rose" />
            <StatCard label="Scor mediu global" value={overview?.average_score || 0} accent="violet" />
            <StatCard label="Admini" value={overview?.staff_users || 0} accent="amber" />
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="NLP attempts" value={overview?.nlp_attempts || 0} accent="emerald" />
            <StatCard label="AI attempts" value={overview?.ai_attempts || 0} accent="violet" />
            <StatCard label="NLP avg score" value={overview?.nlp_average_score || 0} accent="emerald" />
            <StatCard label="AI avg score" value={overview?.ai_average_score || 0} accent="violet" />
          </div>
        </SectionCard>

        <div className="grid min-w-0 gap-6 xl:grid-cols-3">
          <ChartCard
            title="Răspunsuri totale corecte vs greșite"
            subtitle="Distribuția globală a răspunsurilor date de utilizatori în platformă."
          >
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={globalAnswerDistributionData}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={3}
                >
                  {globalAnswerDistributionData.map((entry, index) => (
                    <Cell
                      key={`global-answer-${index}`}
                      fill={ANSWER_COLORS[index % ANSWER_COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard
            title="User vs AI pe moduri"
            subtitle="Comparația scorului mediu dintre utilizatori și AI pe Overall, NLP și AI."
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={globalScoreCompareData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" stroke="#64748b" />
                <YAxis allowDecimals={true} stroke="#64748b" />
                <Tooltip />
                <Bar dataKey="user" radius={[8, 8, 0, 0]}>
                  {globalScoreCompareData.map((_, index) => (
                    <Cell key={`global-user-${index}`} fill={COMPARE_COLORS[0]} />
                  ))}
                </Bar>
                <Bar dataKey="ai" radius={[8, 8, 0, 0]}>
                  {globalScoreCompareData.map((_, index) => (
                    <Cell key={`global-ai-${index}`} fill={COMPARE_COLORS[1]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard
            title="Volum NLP vs AI"
            subtitle="Cum se distribuie încercările între quiz-urile generate cu NLP și AI."
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={globalModeVolumeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="name" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip />
                <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                  {globalModeVolumeData.map((_, index) => (
                    <Cell key={`mode-volume-${index}`} fill={MODE_COLORS[index % MODE_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        <ModeStatsGrid title="AI Solver - Overall" stats={aiOverview?.overall} />
        <ModeStatsGrid title="AI Solver - Quiz-uri NLP" stats={aiOverview?.nlp} />
        <ModeStatsGrid title="AI Solver - Quiz-uri AI" stats={aiOverview?.ai} />

        <SectionCard
          title="Utilizatori"
          subtitle="Vizualizare, statistici rapide și acces la dashboardul fiecărui utilizator."
        >
          <div className="grid gap-4">
            {pagedUsers.map((user) => {
              const isSelected = selectedUserId === user.id
              const isInactive = !user.is_active

              return (
                <div
                  key={user.id}
                  className={`rounded-2xl border p-4 transition ${
                    isSelected
                      ? 'border-brand-300 bg-brand-50/70 shadow-sm'
                      : isInactive
                      ? 'border-rose-200 bg-rose-50/60'
                      : 'border-slate-200 bg-white'
                  }`}
                >
                  <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
                      <div>
                        <p className="text-xs uppercase tracking-wide text-slate-400">Username</p>
                        <p className="mt-1 font-semibold text-slate-950">{user.username}</p>
                      </div>

                      <div>
                        <p className="text-xs uppercase tracking-wide text-slate-400">Email</p>
                        <p className="mt-1 break-all text-slate-700">{user.email}</p>
                      </div>

                      <div>
                        <p className="text-xs uppercase tracking-wide text-slate-400">Nume complet</p>
                        <p className="mt-1 text-slate-700">
                          {`${user.first_name} ${user.last_name}`.trim() || '-'}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs uppercase tracking-wide text-slate-400">Rol / status</p>
                        <p className="mt-1 text-slate-700">
                          {user.is_staff ? 'Admin' : 'User'} · {user.is_active ? 'Activ' : 'Inactiv'}
                        </p>
                      </div>

                      <div>
                        <p className="text-xs uppercase tracking-wide text-slate-400">Statistici</p>
                        <p className="mt-1 text-slate-700">
                          Doc: {user.documents_count} · Sets: {user.question_sets_count} · Attempts: {user.attempts_count} · Avg: {user.average_score}
                        </p>
                      </div>
                    </div>

                    <div className="grid gap-2 sm:grid-cols-2 xl:flex">
                      <button
                        onClick={() => fetchUserDetail(user.id)}
                        className={compactButtonClass(secondaryButtonClass)}
                      >
                        Dashboard
                      </button>

                      {!user.is_staff && (
                        <button
                          onClick={() => setSelectedUser(user)}
                          className={compactButtonClass(
                            user.is_active ? dangerButtonClass : primaryButtonClass
                          )}
                        >
                          {user.is_active ? 'Dezactivează' : 'Activează'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          <Pagination
            page={usersPage}
            totalPages={totalPages(users)}
            onChange={setUsersPage}
          />
        </SectionCard>

        {selectedUserDetail && (
          <>
            <SectionCard
              title={`Dashboard utilizator: ${selectedUserDetail.user.username}`}
              subtitle="Statistici complete pentru utilizatorul selectat, cu accent pe comparația cu AI."
            >
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <StatCard label="Documente" value={selectedUserDetail.documents_count} accent="brand" />
                <StatCard label="Question sets" value={selectedUserDetail.question_sets_count} accent="violet" />
                <StatCard label="Definiții" value={selectedUserDetail.definitions_count} accent="emerald" />
                <StatCard label="Întrebări" value={selectedUserDetail.questions_count} accent="amber" />
              </div>
            </SectionCard>

            <div className="grid min-w-0 gap-6 xl:grid-cols-2">
              <ChartCard
                title="Distribuție dueluri utilizator"
                subtitle="Câte quiz-uri a câștigat utilizatorul, AI-ul sau au fost la egalitate."
              >
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={selectedUserDuelData}
                      dataKey="value"
                      nameKey="name"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={3}
                    >
                      {selectedUserDuelData.map((entry, index) => (
                        <Cell key={`selected-duel-${index}`} fill={USER_DUEL_COLORS[index % USER_DUEL_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </ChartCard>

              <ChartCard
                title="User vs AI pe moduri"
                subtitle="Compară scorul mediu al utilizatorului cu scorul mediu al AI-ului pe Overall, NLP și AI."
              >
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={selectedUserModeCompareData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="name" stroke="#64748b" />
                    <YAxis allowDecimals={true} stroke="#64748b" />
                    <Tooltip />
                    <Bar dataKey="user" radius={[8, 8, 0, 0]}>
                      {selectedUserModeCompareData.map((_, index) => (
                        <Cell key={`selected-user-${index}`} fill={COMPARE_COLORS[0]} />
                      ))}
                    </Bar>
                    <Bar dataKey="ai" radius={[8, 8, 0, 0]}>
                      {selectedUserModeCompareData.map((_, index) => (
                        <Cell key={`selected-ai-${index}`} fill={COMPARE_COLORS[1]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </ChartCard>
            </div>

            <ModeStatsGrid title="User Overall" stats={selectedUserDetail.overall} />
            <ModeStatsGrid title="User NLP" stats={selectedUserDetail.nlp} />
            <ModeStatsGrid title="User AI" stats={selectedUserDetail.ai} />
            <ModeStatsGrid title="AI Solver vs User - Overall" stats={selectedUserDetail.ai_solver_overall} />
            <ModeStatsGrid title="AI Solver vs User - NLP" stats={selectedUserDetail.ai_solver_nlp} />
            <ModeStatsGrid title="AI Solver vs User - AI" stats={selectedUserDetail.ai_solver_ai} />

            <SectionCard
              title="Comparatie user vs AI"
              subtitle="Câte quiz-uri a câștigat utilizatorul comparativ cu AI."
            >
              <div className="grid gap-4 sm:grid-cols-3">
                <StatCard label="Overall user wins" value={selectedUserDetail.user_vs_ai_overall.user_wins} accent="brand" />
                <StatCard label="Overall AI wins" value={selectedUserDetail.user_vs_ai_overall.ai_wins} accent="violet" />
                <StatCard label="Overall ties" value={selectedUserDetail.user_vs_ai_overall.draws} accent="amber" />
              </div>
            </SectionCard>
          </>
        )}

        <SectionCard
          title="Documente"
          subtitle="Toate documentele încărcate în platformă."
        >
          <div className="grid gap-4">
            {pagedDocuments.map((document) => (
              <div
                key={document.id}
                className="rounded-2xl border border-slate-200 bg-white p-4"
              >
                <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                  <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
                    <div>
                      <p className="text-xs uppercase tracking-wide text-slate-400">User</p>
                      <p className="mt-1 font-semibold text-slate-950">{document.username}</p>
                    </div>

                    <div>
                      <p className="text-xs uppercase tracking-wide text-slate-400">Nume complet</p>
                      <p className="mt-1 text-slate-700">{document.full_name || '-'}</p>
                    </div>

                    <div>
                      <p className="text-xs uppercase tracking-wide text-slate-400">Document</p>
                      <p className="mt-1 text-slate-700">#{document.user_document_number}</p>
                    </div>

                    <div>
                      <p className="text-xs uppercase tracking-wide text-slate-400">Fișier</p>
                      <p className="mt-1 break-all text-slate-700">{getDisplayFileName(document.file)}</p>
                    </div>

                    <div>
                      <p className="text-xs uppercase tracking-wide text-slate-400">Stats</p>
                      <p className="mt-1 text-slate-700">
                        Total: {document.definitions_count} · NLP: {document.nlp_definitions_count} · AI: {document.ai_definitions_count} · Sets: {document.question_sets_count}
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={() => setSelectedDocument(document)}
                    className={compactButtonClass(dangerButtonClass)}
                  >
                    Șterge
                  </button>
                </div>
              </div>
            ))}
          </div>

          <Pagination
            page={documentsPage}
            totalPages={totalPages(documents)}
            onChange={setDocumentsPage}
          />
        </SectionCard>

        <SectionCard
          title="Question sets"
          subtitle="Toate seturile generate, separate pe moduri."
        >
          <div className="grid gap-4">
            {pagedQuestionSets.map((item) => (
              <div
                key={item.id}
                className="rounded-2xl border border-slate-200 bg-white p-4"
              >
                <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-6">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">ID</p>
                    <p className="mt-1 font-semibold text-slate-950">#{item.id}</p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">User</p>
                    <p className="mt-1 text-slate-700">{item.username}</p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">Mode</p>
                    <p className="mt-1 text-slate-700">{item.generation_mode.toUpperCase()}</p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">Dificultate</p>
                    <p className="mt-1 text-slate-700">{item.difficulty}</p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">Întrebări</p>
                    <p className="mt-1 text-slate-700">{item.questions_count}</p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">Data</p>
                    <p className="mt-1 text-slate-700">{formatDateTime(item.created_at)}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <Pagination
            page={questionSetsPage}
            totalPages={totalPages(questionSets)}
            onChange={setQuestionSetsPage}
          />
        </SectionCard>

        <SectionCard
          title="Quiz Attempts"
          subtitle="Istoricul global al încercărilor de quiz, inclusiv scorul AI."
        >
          <div className="grid gap-4">
            {pagedAttempts.map((attempt) => (
              <div
                key={attempt.id}
                className="rounded-2xl border border-slate-200 bg-white p-4"
              >
                <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-6">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">User</p>
                    <p className="mt-1 font-semibold text-slate-950">{attempt.username}</p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">Attempt / document</p>
                    <p className="mt-1 text-slate-700">
                      #{attempt.user_attempt_number} · Doc #{attempt.user_document_number}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">Mode / dificultate</p>
                    <p className="mt-1 text-slate-700">
                      {attempt.generation_mode.toUpperCase()} · {attempt.difficulty}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">Scor user</p>
                    <p className="mt-1 text-slate-700">{attempt.score} / {attempt.total_questions}</p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">Scor AI</p>
                    <p className="mt-1 text-slate-700">
                      {attempt.ai_score ?? '-'}{attempt.ai_score !== null ? ` / ${attempt.total_questions}` : ''}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">Timp / data</p>
                    <p className="mt-1 text-slate-700">{formatDateTime(attempt.completed_at)}</p>
                    {attempt.time_spent_seconds !== undefined && (
                      <p className="mt-1 text-xs text-slate-500">
                        User: {formatDuration(attempt.time_spent_seconds)}
                      </p>
                    )}
                    {attempt.ai_time_spent_seconds !== undefined && (
                      <p className="mt-1 text-xs text-slate-500">
                        AI: {formatDuration(attempt.ai_time_spent_seconds)}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <Pagination
            page={attemptsPage}
            totalPages={totalPages(attempts)}
            onChange={setAttemptsPage}
          />
        </SectionCard>
      </div>
    </PageContainer>
  )
}