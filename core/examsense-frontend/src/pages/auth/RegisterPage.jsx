import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import ErrorAlert from '../../components/common/ErrorAlert'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../hooks/useToast'
import usePageTitle from '../../hooks/usePageTitle'
import { getApiErrorMessages } from '../../utils/errorMessages'
import { validateEmail } from '../../utils/validators'

const benefits = [
  'Îți creezi rapid cont și începi să încarci documente',
  'Generezi quiz-uri cu NLP sau AI',
  'Urmărești progresul și scorurile în dashboard',
  'Compari performanța ta cu un solver AI',
]

export default function RegisterPage() {
  usePageTitle('Înregistrare')

  const navigate = useNavigate()
  const { register } = useAuth()
  const { showToast } = useToast()

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    password: '',
    password_confirm: '',
  })

  const [touched, setTouched] = useState({})
  const [errors, setErrors] = useState([])
  const [isSubmitting, setIsSubmitting] = useState(false)

  const liveErrors = useMemo(() => {
    const nextErrors = {}

    if (!formData.first_name.trim()) {
      nextErrors.first_name = 'Prenumele este obligatoriu.'
    }

    if (!formData.last_name.trim()) {
      nextErrors.last_name = 'Numele este obligatoriu.'
    }

    if (!formData.username.trim()) {
      nextErrors.username = 'Username-ul este obligatoriu.'
    }

    const emailError = validateEmail(formData.email)
    if (emailError) {
      nextErrors.email = emailError
    }

    if (!formData.password.trim()) {
      nextErrors.password = 'Parola este obligatorie.'
    } else if (formData.password.length < 8) {
      nextErrors.password = 'Parola trebuie să aibă minimum 8 caractere.'
    }

    if (!formData.password_confirm.trim()) {
      nextErrors.password_confirm = 'Confirmarea parolei este obligatorie.'
    } else if (formData.password_confirm !== formData.password) {
      nextErrors.password_confirm = 'Parolele nu coincid.'
    }

    return nextErrors
  }, [formData])

  function handleChange(e) {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

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
      first_name: true,
      last_name: true,
      username: true,
      email: true,
      password: true,
      password_confirm: true,
    })

    if (Object.keys(liveErrors).length > 0) {
      showToast('Verifică datele introduse.', 'error')
      return
    }

    setIsSubmitting(true)

    try {
      await register({
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        username: formData.username.trim(),
        email: formData.email.trim(),
        password: formData.password,
        password_confirm: formData.password_confirm,
      })

      showToast('Cont creat cu succes. Te poți autentifica.', 'success')
      navigate('/login')
    } catch (err) {
      const parsedErrors = getApiErrorMessages(err, 'Înregistrarea a eșuat.')
      setErrors(parsedErrors)
      showToast('Înregistrarea a eșuat.', 'error')
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
              Creează-ți contul
            </span>

            <h1 className="mt-5 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
              Începe să folosești{' '}
              <span className="bg-linear-to-r from-brand-600 via-violet-600 to-cyan-500 bg-clip-text text-transparent">
                ExamSense+
              </span>{' '}
              pentru învățare, quiz-uri și comparație User vs AI.
            </h1>

            <p className="mt-4 max-w-xl text-sm leading-7 text-slate-600 sm:text-base">
              Creează un cont și transformă rapid documentele tale în materiale interactive de studiu.
            </p>

            <div className="mt-6 grid gap-3">
              {benefits.map((item) => (
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
          title="Înregistrare"
          subtitle="Completează formularul și creează-ți contul."
          className="min-w-0"
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Prenume
                </label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  onBlur={() => handleBlur('first_name')}
                  autoComplete="given-name"
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  placeholder="Prenume"
                />
                {touched.first_name && liveErrors.first_name && (
                  <p className="mt-2 text-xs text-rose-600">{liveErrors.first_name}</p>
                )}
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Nume
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  onBlur={() => handleBlur('last_name')}
                  autoComplete="family-name"
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  placeholder="Nume"
                />
                {touched.last_name && liveErrors.last_name && (
                  <p className="mt-2 text-xs text-rose-600">{liveErrors.last_name}</p>
                )}
              </div>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Username
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                onBlur={() => handleBlur('username')}
                autoComplete="username"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                placeholder="Alege un username"
              />
              {touched.username && liveErrors.username && (
                <p className="mt-2 text-xs text-rose-600">{liveErrors.username}</p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                onBlur={() => handleBlur('email')}
                autoComplete="email"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                placeholder="nume@email.com"
              />
              {touched.email && liveErrors.email && (
                <p className="mt-2 text-xs text-rose-600">{liveErrors.email}</p>
              )}
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Parolă
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  onBlur={() => handleBlur('password')}
                  autoComplete="new-password"
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  placeholder="Introdu parola"
                />
                {touched.password && liveErrors.password && (
                  <p className="mt-2 text-xs text-rose-600">{liveErrors.password}</p>
                )}
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Confirmă parola
                </label>
                <input
                  type="password"
                  name="password_confirm"
                  value={formData.password_confirm}
                  onChange={handleChange}
                  onBlur={() => handleBlur('password_confirm')}
                  autoComplete="new-password"
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  placeholder="Confirmă parola"
                />
                {touched.password_confirm && liveErrors.password_confirm && (
                  <p className="mt-2 text-xs text-rose-600">
                    {liveErrors.password_confirm}
                  </p>
                )}
              </div>
            </div>

            <ErrorAlert messages={errors} />

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-2xl bg-slate-950 px-6 py-3.5 text-sm font-medium text-white transition hover:opacity-95 disabled:opacity-70"
            >
              {isSubmitting ? 'Se creează contul...' : 'Creează cont'}
            </button>

            <p className="text-center text-sm text-slate-500">
              Ai deja cont?{' '}
              <Link to="/login" className="font-medium text-brand-600 hover:text-brand-700">
                Autentifică-te
              </Link>
            </p>
          </form>
        </SectionCard>
      </div>
    </PageContainer>
  )
}