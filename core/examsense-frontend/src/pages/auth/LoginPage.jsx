import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import ErrorAlert from '../../components/common/ErrorAlert'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../hooks/useToast'
import usePageTitle from '../../hooks/usePageTitle'
import { getApiErrorMessages } from '../../utils/errorMessages'

const leftHighlights = [
  'Autentificare rapidă și sigură',
  'Acces la quiz-uri generate automat',
  'Comparație directă între User și AI',
  'Istoric, scoruri și progres centralizat',
]

export default function LoginPage() {
  usePageTitle('Autentificare')

  const navigate = useNavigate()
  const { login } = useAuth()
  const { showToast } = useToast()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [touched, setTouched] = useState({})
  const [errors, setErrors] = useState([])
  const [isSubmitting, setIsSubmitting] = useState(false)

  const usernameError = useMemo(() => {
    if (!username.trim()) {
      return 'Username-ul este obligatoriu.'
    }
    return ''
  }, [username])

  const passwordError = useMemo(() => {
    if (!password.trim()) {
      return 'Parola este obligatorie.'
    }
    return ''
  }, [password])

  function handleBlur(fieldName) {
    setTouched((prev) => ({
      ...prev,
      [fieldName]: true,
    }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setErrors([])
    setTouched({
      username: true,
      password: true,
    })

    if (usernameError || passwordError) {
      showToast('Verifică datele introduse.', 'error')
      return
    }

    setIsSubmitting(true)

    try {
      await login(username.trim(), password)
      showToast('Autentificare reușită.', 'success')
      navigate('/documents')
    } catch (err) {
      const parsedErrors = getApiErrorMessages(err, 'Autentificarea a eșuat.')
      setErrors(parsedErrors)
      showToast('Autentificarea a eșuat.', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <PageContainer>
      <div className="grid gap-8 py-8 lg:grid-cols-[0.95fr_1.05fr] lg:py-12">
        <div className="min-w-0">
          <div className="rounded-[30px] border border-brand-100 bg-linear-to-br from-brand-50 via-violet-50 to-white p-6 shadow-sm sm:p-8">
            <span className="inline-flex rounded-full border border-brand-200 bg-white/80 px-4 py-1.5 text-sm font-medium text-brand-700">
              Bine ai revenit
            </span>

            <h1 className="mt-5 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
              Intră în contul tău și continuă să înveți cu{' '}
              <span className="bg-linear-to-r from-brand-600 via-violet-600 to-cyan-500 bg-clip-text text-transparent">
                ExamSense+
              </span>
              .
            </h1>

            <p className="mt-4 max-w-xl text-sm leading-7 text-slate-600 sm:text-base">
              Autentifică-te pentru a încărca documente, a genera quiz-uri și a vedea cum te compari
              cu un solver AI pe aceleași întrebări.
            </p>

            <div className="mt-6 grid gap-3">
              {leftHighlights.map((item) => (
                <div
                  key={item}
                  className="rounded-2xl border border-white/70 bg-white/80 px-4 py-3 text-sm font-medium text-slate-700 shadow-xs"
                >
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>

        <SectionCard
          title="Autentificare"
          subtitle="Introdu username-ul și parola pentru a accesa aplicația."
          className="min-w-0"
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onBlur={() => handleBlur('username')}
                autoComplete="username"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                placeholder="Introdu username-ul"
              />
              {touched.username && usernameError && (
                <p className="mt-2 text-xs text-rose-600">{usernameError}</p>
              )}
            </div>

            <div>
              <div className="mb-2 flex items-center justify-between gap-3">
                <label className="block text-sm font-medium text-slate-700">
                  Parolă
                </label>
                <Link
                  to="/forgot-password"
                  className="text-xs font-medium text-brand-600 hover:text-brand-700"
                >
                  Ai uitat parola?
                </Link>
              </div>

              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onBlur={() => handleBlur('password')}
                autoComplete="current-password"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                placeholder="Introdu parola"
              />
              {touched.password && passwordError && (
                <p className="mt-2 text-xs text-rose-600">{passwordError}</p>
              )}
            </div>

            <ErrorAlert messages={errors} />

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-2xl bg-slate-950 px-6 py-3.5 text-sm font-medium text-white transition hover:opacity-95 disabled:opacity-70"
            >
              {isSubmitting ? 'Se autentifică...' : 'Autentificare'}
            </button>

            <p className="text-center text-sm text-slate-500">
              Nu ai cont?{' '}
              <Link to="/register" className="font-medium text-brand-600 hover:text-brand-700">
                Creează unul acum
              </Link>
            </p>
          </form>
        </SectionCard>
      </div>
    </PageContainer>
  )
}