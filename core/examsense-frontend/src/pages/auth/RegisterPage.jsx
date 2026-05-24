import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff } from 'lucide-react'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import ErrorAlert from '../../components/common/ErrorAlert'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../hooks/useToast'
import { getApiErrorMessages } from '../../utils/errorMessages'
import { primaryButtonClass } from '../../utils/buttonClasses'
import {
  validateEmail,
  validateStrongPassword,
  validatePasswordMatch,
  validateUsername,
  validateRequiredText,
} from '../../utils/validators'

export default function RegisterPage() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const { showToast } = useToast()

  const [form, setForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    password_confirm: '',
  })

  const [touched, setTouched] = useState({})
  const [errors, setErrors] = useState([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false)

  const liveErrors = useMemo(() => {
    return {
      username: validateUsername(form.username),
      email: validateEmail(form.email),
      first_name: validateRequiredText(form.first_name, 'Prenumele'),
      last_name: validateRequiredText(form.last_name, 'Numele'),
      password: validateStrongPassword(form.password),
      password_confirm: validatePasswordMatch(form.password, form.password_confirm),
    }
  }, [form])

  const hasLiveErrors = Object.values(liveErrors).some(Boolean)

  function handleChange(e) {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
  }

  function handleBlur(e) {
    setTouched((prev) => ({
      ...prev,
      [e.target.name]: true,
    }))
  }

  function fieldError(name) {
    return touched[name] ? liveErrors[name] : ''
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setErrors([])
    setTouched({
      username: true,
      email: true,
      first_name: true,
      last_name: true,
      password: true,
      password_confirm: true,
    })

    if (hasLiveErrors) {
      showToast('Verifică datele introduse înainte de continuare.', 'error')
      return
    }

    setIsSubmitting(true)

    try {
      await register(form)
      showToast('Cont creat cu succes. Te poți autentifica acum.', 'success')
      navigate('/login')
    } catch (err) {
      const parsedErrors = getApiErrorMessages(err, 'Înregistrarea a eșuat. Verifică datele.')
      setErrors(parsedErrors)
      showToast('Înregistrarea a eșuat.', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <PageContainer>
      <div className="mx-auto max-w-2xl py-8 sm:py-12">
        <SectionCard
          title="Creează cont"
          subtitle="Construiește-ți spațiul tău de învățare în ExamSense+."
        >
          <form onSubmit={handleSubmit} className="grid gap-5 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="mb-2 block text-sm font-medium text-slate-700">Username</label>
              <input
                name="username"
                value={form.username}
                onChange={handleChange}
                onBlur={handleBlur}
                autoComplete="username"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                placeholder="Ex: rares01"
              />
              {fieldError('username') ? (
                <p className="mt-2 text-xs text-rose-600">{fieldError('username')}</p>
              ) : (
                <p className="mt-2 text-xs text-slate-500">
                  Alege un username unic, ușor de recunoscut.
                </p>
              )}
            </div>

            <div className="sm:col-span-2">
              <label className="mb-2 block text-sm font-medium text-slate-700">Email</label>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                onBlur={handleBlur}
                autoComplete="email"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                placeholder="Ex: nume@email.com"
              />
              {fieldError('email') ? (
                <p className="mt-2 text-xs text-rose-600">{fieldError('email')}</p>
              ) : (
                <p className="mt-2 text-xs text-slate-500">
                  Folosește o adresă validă de email.
                </p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Prenume</label>
              <input
                name="first_name"
                value={form.first_name}
                onChange={handleChange}
                onBlur={handleBlur}
                autoComplete="given-name"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                placeholder="Ex: Rareș"
              />
              {fieldError('first_name') && (
                <p className="mt-2 text-xs text-rose-600">{fieldError('first_name')}</p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Nume</label>
              <input
                name="last_name"
                value={form.last_name}
                onChange={handleChange}
                onBlur={handleBlur}
                autoComplete="family-name"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                placeholder="Ex: Popescu"
              />
              {fieldError('last_name') && (
                <p className="mt-2 text-xs text-rose-600">{fieldError('last_name')}</p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Parolă</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={form.password}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  autoComplete="new-password"
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3 pr-12 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  placeholder="Introdu o parolă puternică"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-800"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {fieldError('password') ? (
                <p className="mt-2 text-xs text-rose-600">{fieldError('password')}</p>
              ) : (
                <p className="mt-2 text-xs text-slate-500">
                  Minim 8 caractere, cu literă mare, literă mică și cifră.
                </p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Confirmă parola</label>
              <div className="relative">
                <input
                  type={showPasswordConfirm ? 'text' : 'password'}
                  name="password_confirm"
                  value={form.password_confirm}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  autoComplete="new-password"
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3 pr-12 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  placeholder="Reintrodu parola"
                />
                <button
                  type="button"
                  onClick={() => setShowPasswordConfirm((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-800"
                >
                  {showPasswordConfirm ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {fieldError('password_confirm') && (
                <p className="mt-2 text-xs text-rose-600">{fieldError('password_confirm')}</p>
              )}
            </div>

            <div className="sm:col-span-2">
              <ErrorAlert messages={errors} />
            </div>

            <div className="sm:col-span-2">
              <button disabled={isSubmitting} className={`w-full ${primaryButtonClass}`}>
                {isSubmitting ? 'Se creează contul...' : 'Register'}
              </button>
            </div>

            <p className="sm:col-span-2 text-center text-sm text-slate-500">
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