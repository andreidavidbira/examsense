import { useEffect, useState } from 'react'

import api from '../../api/axios'
import ConfirmDialog from '../../components/common/ConfirmDialog'
import ErrorAlert from '../../components/common/ErrorAlert'
import PageLoader from '../../components/common/PageLoader'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import { useToast } from '../../hooks/useToast'
import usePageTitle from '../../hooks/usePageTitle'
import {
  dangerButtonClass,
  secondaryButtonClass,
} from '../../utils/buttonClasses'
import { getDisplayFileName } from '../../utils/fileHelpers'

// afisam un card simplu pentru statisticile din dashboardul de admin
function StatCard({ label, value }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
    </div>
  )
}

export default function AdminDashboardPage() {
  usePageTitle('Panoul de administrare')
  const { showToast } = useToast()

  const [overview, setOverview] = useState(null)
  const [users, setUsers] = useState([])
  const [documents, setDocuments] = useState([])
  const [attempts, setAttempts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [selectedUser, setSelectedUser] = useState(null)
  const [selectedDocument, setSelectedDocument] = useState(null)

  // incarcam toate datele necesare pentru panoul de administrare
  async function fetchAll() {
    try {
      setLoading(true)

      const [
        overviewResponse,
        usersResponse,
        documentsResponse,
        attemptsResponse,
      ] = await Promise.all([
        api.get('/adminpanel/overview/'),
        api.get('/adminpanel/users/'),
        api.get('/adminpanel/documents/'),
        api.get('/adminpanel/attempts/'),
      ])

      setOverview(overviewResponse.data)
      setUsers(usersResponse.data.results || [])
      setDocuments(documentsResponse.data.results || [])
      setAttempts(attemptsResponse.data.results || [])
      setError('')
    } catch {
      setError('Nu am putut încărca panoul de administrare.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAll()
  }, [])

  // schimbam starea activa sau inactiva a utilizatorului selectat
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

  // stergem documentul selectat din panoul de admin
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
          subtitle="Statistici globale și management pentru utilizatori, documente și quiz-uri."
        >
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="Utilizatori" value={overview?.total_users || 0} />
            <StatCard label="Utilizatori activi" value={overview?.active_users || 0} />
            <StatCard label="Documente totale" value={overview?.total_documents || 0} />
            <StatCard label="Quiz attempts" value={overview?.total_attempts || 0} />
          </div>

          <div className="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="Admini" value={overview?.staff_users || 0} />
            <StatCard label="Definiții extrase" value={overview?.total_definitions || 0} />
            <StatCard label="Întrebări generate" value={overview?.total_questions || 0} />
            <StatCard label="Scor mediu global" value={overview?.average_score || 0} />
          </div>
        </SectionCard>

        <SectionCard
          title="Utilizatori"
          subtitle="Vizualizare și control asupra utilizatorilor existenți."
        >
          <div className="overflow-x-auto">
            <div className="min-w-240">
              <div className="grid grid-cols-8 gap-3 rounded-2xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700">
                <div>Username</div>
                <div>Email</div>
                <div>Nume complet</div>
                <div>Rol</div>
                <div>Status</div>
                <div>Documente</div>
                <div>Attempts</div>
                <div>Acțiuni</div>
              </div>

              <div className="mt-3 space-y-3">
                {users.map((user) => (
                  <div
                    key={user.id}
                    className="grid grid-cols-8 gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 text-sm text-slate-700"
                  >
                    <div className="font-medium text-slate-950">{user.username}</div>
                    <div className="break-all">{user.email}</div>
                    <div>{`${user.first_name} ${user.last_name}`.trim() || '-'}</div>
                    <div>{user.is_staff ? 'Admin' : 'User'}</div>
                    <div>{user.is_active ? 'Activ' : 'Inactiv'}</div>
                    <div>{user.documents_count}</div>
                    <div>{user.attempts_count}</div>
                    <div>
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

        <SectionCard
          title="Documente"
          subtitle="Toate documentele încărcate în platformă."
        >
          <div className="overflow-x-auto">
            <div className="min-w-275">
              <div className="grid grid-cols-8 gap-3 rounded-2xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700">
                <div>User</div>
                <div>Nume complet</div>
                <div>Email</div>
                <div>Document #</div>
                <div>Fișier</div>
                <div>Definiții</div>
                <div>Întrebări</div>
                <div>Acțiuni</div>
              </div>

              <div className="mt-3 space-y-3">
                {documents.map((document) => (
                  <div
                    key={document.id}
                    className="grid grid-cols-8 gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 text-sm text-slate-700"
                  >
                    <div className="font-medium text-slate-950">{document.username}</div>
                    <div>{document.full_name || '-'}</div>
                    <div className="break-all">{document.email}</div>
                    <div>#{document.user_document_number}</div>
                    <div className="break-all">{getDisplayFileName(document.file)}</div>
                    <div>{document.definitions_count}</div>
                    <div>{document.questions_count}</div>
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
          title="Quiz Attempts"
          subtitle="Istoricul global al încercărilor de quiz."
        >
          <div className="overflow-x-auto">
            <div className="min-w-250">
              <div className="grid grid-cols-7 gap-3 rounded-2xl bg-slate-100 px-4 py-3 text-sm font-semibold text-slate-700">
                <div>User</div>
                <div>Nume complet</div>
                <div>Email</div>
                <div>Attempt #</div>
                <div>Document #</div>
                <div>Scor</div>
                <div>Dată</div>
              </div>

              <div className="mt-3 space-y-3">
                {attempts.map((attempt) => (
                  <div
                    key={attempt.id}
                    className="grid grid-cols-7 gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-4 text-sm text-slate-700"
                  >
                    <div className="font-medium text-slate-950">{attempt.username}</div>
                    <div>{attempt.full_name || '-'}</div>
                    <div className="break-all">{attempt.email}</div>
                    <div>#{attempt.user_attempt_number}</div>
                    <div>#{attempt.user_document_number}</div>
                    <div>{attempt.score} / {attempt.total_questions}</div>
                    <div>{new Date(attempt.completed_at).toLocaleString()}</div>
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