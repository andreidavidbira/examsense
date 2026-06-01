import { useEffect, useState } from 'react'

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
  secondaryButtonClass,
} from '../../utils/buttonClasses'
import { getDisplayFileName } from '../../utils/fileHelpers'

function ModeStatsGrid({ title, stats }) {
  if (!stats) return null

  return (
    <SectionCard title={title}>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
        <StatCard label="Attempts" value={stats.attempts_count} />
        <StatCard label="Corecte" value={stats.correct_answers} />
        <StatCard label="Greșite" value={stats.wrong_answers} />
        <StatCard label="Scor mediu" value={stats.average_score} />
        <StatCard label="Scor maxim" value={stats.best_score} />
        <StatCard label="Scor minim" value={stats.worst_score} />
      </div>
    </SectionCard>
  )
}

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

  async function fetchUserDetail(userId) {
    try {
      const response = await api.get(`/adminpanel/users/${userId}/`)
      setSelectedUserDetail(response.data)
    } catch {
      showToast('Nu am putut încărca dashboardul utilizatorului.', 'error')
    }
  }

  useEffect(() => {
    fetchAll()
  }, [])

  async function handleToggleUserActive() {
    if (!selectedUser) return

    try {
      await api.patch(`/adminpanel/users/${selectedUser.id}/toggle-active/`, {
        is_active: !selectedUser.is_active,
      })

      showToast('Starea utilizatorului a fost actualizată.', 'success')
      setSelectedUser(null)
      fetchAll()
    } catch {
      showToast('Nu am putut actualiza utilizatorul.', 'error')
    }
  }

  async function handleDeleteDocument() {
    if (!selectedDocument) return

    try {
      await api.delete(`/adminpanel/documents/${selectedDocument.id}/delete/`)
      showToast('Documentul a fost șters.', 'success')
      setSelectedDocument(null)
      fetchAll()
    } catch {
      showToast('Nu am putut șterge documentul.', 'error')
    }
  }

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
        <SectionCard
          title="Admin Control Panel"
          subtitle="Statistici globale, comparații NLP vs AI și management pentru utilizatori."
        >
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <StatCard label="Utilizatori" value={overview?.total_users || 0} />
            <StatCard label="Utilizatori activi" value={overview?.active_users || 0} />
            <StatCard label="Documente totale" value={overview?.total_documents || 0} />
            <StatCard label="Question sets" value={overview?.total_question_sets || 0} />
            <StatCard label="Attempts" value={overview?.total_attempts || 0} />
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <StatCard label="Răspunsuri totale" value={overview?.total_answers || 0} />
            <StatCard label="Corecte" value={overview?.correct_answers || 0} />
            <StatCard label="Greșite" value={overview?.wrong_answers || 0} />
            <StatCard label="Scor mediu global" value={overview?.average_score || 0} />
            <StatCard label="Admini" value={overview?.staff_users || 0} />
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="NLP attempts" value={overview?.nlp_attempts || 0} />
            <StatCard label="AI attempts" value={overview?.ai_attempts || 0} />
            <StatCard label="NLP avg score" value={overview?.nlp_average_score || 0} />
            <StatCard label="AI avg score" value={overview?.ai_average_score || 0} />
          </div>
        </SectionCard>

        <ModeStatsGrid title="AI Solver - Overall" stats={aiOverview?.overall} />
        <ModeStatsGrid title="AI Solver - Quiz-uri NLP" stats={aiOverview?.nlp} />
        <ModeStatsGrid title="AI Solver - Quiz-uri AI" stats={aiOverview?.ai} />

        <SectionCard
          title="Utilizatori"
          subtitle="Vizualizare, statistici rapide și acces la dashboardul fiecărui utilizator."
        >
          <div className="overflow-x-auto">
            <div className="min-w-[1150px]">
              <div className="grid grid-cols-10 gap-3 rounded-2xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700">
                <div>Username</div>
                <div>Email</div>
                <div>Nume complet</div>
                <div>Rol</div>
                <div>Status</div>
                <div>Documente</div>
                <div>Sets</div>
                <div>Attempts</div>
                <div>Scor mediu</div>
                <div>Acțiuni</div>
              </div>

              <div className="mt-3 space-y-3">
                {users.map((user) => (
                  <div
                    key={user.id}
                    className="grid grid-cols-10 gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 text-sm text-slate-700"
                  >
                    <div className="font-medium text-slate-950">{user.username}</div>
                    <div className="break-all">{user.email}</div>
                    <div>{`${user.first_name} ${user.last_name}`.trim() || '-'}</div>
                    <div>{user.is_staff ? 'Admin' : 'User'}</div>
                    <div>{user.is_active ? 'Activ' : 'Inactiv'}</div>
                    <div>{user.documents_count}</div>
                    <div>{user.question_sets_count}</div>
                    <div>{user.attempts_count}</div>
                    <div>{user.average_score}</div>
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => fetchUserDetail(user.id)}
                        className={secondaryButtonClass}
                      >
                        Dashboard
                      </button>

                      {!user.is_staff && (
                        <button
                          onClick={() => setSelectedUser(user)}
                          className={secondaryButtonClass}
                        >
                          {user.is_active ? 'Dezactivează' : 'Activează'}
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </SectionCard>

        {selectedUserDetail && (
          <>
            <SectionCard
              title={`Dashboard utilizator: ${selectedUserDetail.user.username}`}
              subtitle="Statistici complete pentru utilizatorul selectat."
            >
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <StatCard label="Documente" value={selectedUserDetail.documents_count} />
                <StatCard label="Question sets" value={selectedUserDetail.question_sets_count} />
                <StatCard label="Definiții" value={selectedUserDetail.definitions_count} />
                <StatCard label="Întrebări" value={selectedUserDetail.questions_count} />
              </div>
            </SectionCard>

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
                <StatCard label="Overall user wins" value={selectedUserDetail.user_vs_ai_overall.user_wins} />
                <StatCard label="Overall AI wins" value={selectedUserDetail.user_vs_ai_overall.ai_wins} />
                <StatCard label="Overall ties" value={selectedUserDetail.user_vs_ai_overall.draws} />
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-3">
                <StatCard label="NLP user wins" value={selectedUserDetail.user_vs_ai_nlp.user_wins} />
                <StatCard label="NLP AI wins" value={selectedUserDetail.user_vs_ai_nlp.ai_wins} />
                <StatCard label="NLP ties" value={selectedUserDetail.user_vs_ai_nlp.draws} />
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-3">
                <StatCard label="AI user wins" value={selectedUserDetail.user_vs_ai_ai.user_wins} />
                <StatCard label="AI AI wins" value={selectedUserDetail.user_vs_ai_ai.ai_wins} />
                <StatCard label="AI ties" value={selectedUserDetail.user_vs_ai_ai.draws} />
              </div>
            </SectionCard>

            <SectionCard
              title="Concepte slabe"
              subtitle="Conceptele la care utilizatorul greșește cel mai des."
            >
              <div className="grid gap-4 md:grid-cols-2">
                {selectedUserDetail.most_wrong_concepts.map((item, index) => (
                  <div
                    key={`${item.concept}-${index}`}
                    className="rounded-2xl border border-slate-200 bg-white p-4"
                  >
                    <p className="text-lg font-semibold text-slate-950">{item.concept}</p>
                    <p className="mt-2 text-sm text-slate-500">Greșit de {item.wrong_count} ori</p>
                  </div>
                ))}
              </div>
            </SectionCard>
          </>
        )}

        <SectionCard
          title="Documente"
          subtitle="Toate documentele încărcate în platformă."
        >
          <div className="overflow-x-auto">
            <div className="min-w-[1200px]">
              <div className="grid grid-cols-10 gap-3 rounded-2xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700">
                <div>User</div>
                <div>Nume complet</div>
                <div>Email</div>
                <div>Document #</div>
                <div>Fișier</div>
                <div>Def. total</div>
                <div>NLP</div>
                <div>AI</div>
                <div>Sets</div>
                <div>Acțiuni</div>
              </div>

              <div className="mt-3 space-y-3">
                {documents.map((document) => (
                  <div
                    key={document.id}
                    className="grid grid-cols-10 gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 text-sm text-slate-700"
                  >
                    <div className="font-medium text-slate-950">{document.username}</div>
                    <div>{document.full_name || '-'}</div>
                    <div className="break-all">{document.email}</div>
                    <div>#{document.user_document_number}</div>
                    <div className="break-all">{getDisplayFileName(document.file)}</div>
                    <div>{document.definitions_count}</div>
                    <div>{document.nlp_definitions_count}</div>
                    <div>{document.ai_definitions_count}</div>
                    <div>{document.question_sets_count}</div>
                    <div>
                      <button
                        onClick={() => setSelectedDocument(document)}
                        className={dangerButtonClass}
                      >
                        Șterge
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="Question sets"
          subtitle="Toate seturile generate, separate pe moduri."
        >
          <div className="overflow-x-auto">
            <div className="min-w-[900px]">
              <div className="grid grid-cols-6 gap-3 rounded-2xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700">
                <div>ID</div>
                <div>User</div>
                <div>Mode</div>
                <div>Dificultate</div>
                <div>Întrebări</div>
                <div>Data</div>
              </div>

              <div className="mt-3 space-y-3">
                {questionSets.map((item) => (
                  <div
                    key={item.id}
                    className="grid grid-cols-6 gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 text-sm text-slate-700"
                  >
                    <div>#{item.id}</div>
                    <div>{item.username}</div>
                    <div>{item.generation_mode.toUpperCase()}</div>
                    <div>{item.difficulty}</div>
                    <div>{item.questions_count}</div>
                    <div>{new Date(item.created_at).toLocaleString()}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </SectionCard>

        <SectionCard
          title="Quiz Attempts"
          subtitle="Istoricul global al încercărilor de quiz, inclusiv scorul AI."
        >
          <div className="overflow-x-auto">
            <div className="min-w-[1200px]">
              <div className="grid grid-cols-9 gap-3 rounded-2xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700">
                <div>User</div>
                <div>Nume complet</div>
                <div>Email</div>
                <div>Attempt #</div>
                <div>Document #</div>
                <div>Mode</div>
                <div>Dificultate</div>
                <div>Scor user</div>
                <div>Scor AI</div>
              </div>

              <div className="mt-3 space-y-3">
                {attempts.map((attempt) => (
                  <div
                    key={attempt.id}
                    className="grid grid-cols-9 gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 text-sm text-slate-700"
                  >
                    <div className="font-medium text-slate-950">{attempt.username}</div>
                    <div>{attempt.full_name || '-'}</div>
                    <div className="break-all">{attempt.email}</div>
                    <div>#{attempt.user_attempt_number}</div>
                    <div>#{attempt.user_document_number}</div>
                    <div>{attempt.generation_mode.toUpperCase()}</div>
                    <div>{attempt.difficulty}</div>
                    <div>{attempt.score} / {attempt.total_questions}</div>
                    <div>{attempt.ai_score ?? '-'}{attempt.ai_score !== null ? ` / ${attempt.total_questions}` : ''}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </SectionCard>
      </div>
    </PageContainer>
  )
}