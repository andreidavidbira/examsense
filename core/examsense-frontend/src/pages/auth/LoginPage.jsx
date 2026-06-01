import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Eye, EyeOff } from 'lucide-react'

import ErrorAlert from '../../components/common/ErrorAlert'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../hooks/useToast'
import usePageTitle from '../../hooks/usePageTitle'
import { primaryButtonClass } from '../../utils/buttonClasses'
import { getApiErrorMessages } from '../../utils/errorMessages'
import {
  validateRequiredText,
  validateUsername,
} from '../../utils/validators'

// afisam formularul de autentificare si validam datele introduse
export default function LoginPage() {
  usePageTitle('Login')

  const navigate = useNavigate()
  const { login } = useAuth()
  const { showToast } = useToast()

  const [form, setForm] = useState({
    username: '',
    password: '',
  })
  const [touched, setTouched] = useState({})
  const [errors, setErrors] = useState([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  // validam live campurile necesare pentru autentificare
  const liveErrors = useMemo(() => {
    return {
      username: validateUsername(form.username),
      password: validateRequiredText(form.password, 'Parola'),
    }
  }, [form])

  const hasLiveErrors = Object.values(liveErrors).some(Boolean)

  // actualizam campul modificat in formular
  function handleChange(e) {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
  }

  // marcam un camp ca fiind atins pentru afisarea erorilor
  function handleBlur(e) {
    setTouched((prev) => ({
      ...prev,
      [e.target.name]: true,
    }))
  }

  function fieldError(name) {
    return touched[name] ? liveErrors[name] : ''
  }

  // trimitem datele de login si redirectionam utilizatorul dupa autentificare
  async function handleSubmit(e) {
    e.preventDefault()
    setErrors([])
    setTouched({
      username: true,
      password: true,
    })

    if (hasLiveErrors) {
      showToast('Completeaza corect datele pentru autentificare.', 'error')
      return
    }

    setIsSubmitting(true)

    try {
      await login(form.username, form.password)
      showToast('Autentificare reusita.', 'success')
      navigate('/documents')
    } catch (err) {
      const parsedErrors = getApiErrorMessages(
        err,
        'Autentificare esuata. Verifica datele introduse.'
      )
      setErrors(parsedErrors)
      showToast('Autentificare esuata.', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <PageContainer>
      <div className="mx-auto max-w-xl py-8 sm:py-12">
        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
          <SectionCard
            title="Autentificare"
            subtitle="Intra in contul tau ExamSense+ pentru a continua."
          >
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Username
                </label>
                <input
                  name="username"
                  value={form.username}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  autoComplete="username"
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                  placeholder="Introdu username-ul"
                />
                {fieldError('username') && (
                  <p className="mt-2 text-xs text-rose-600">{fieldError('username')}</p>
                )}
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Parola
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    autoComplete="current-password"
                    className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 pr-12 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                    placeholder="Introdu parola"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-800"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
                {fieldError('password') && (
                  <p className="mt-2 text-xs text-rose-600">{fieldError('password')}</p>
                )}
              </div>

              <div className="text-right">
                <Link
                  to="/forgot-password"
                  className="text-sm font-medium text-brand-600 hover:text-brand-700"
                >
                  Ai uitat parola?
                </Link>
              </div>

              <ErrorAlert messages={errors} />

              <button disabled={isSubmitting} className={`w-full ${primaryButtonClass}`}>
                {isSubmitting ? 'Se autentifica...' : 'Login'}
              </button>

              <p className="text-center text-sm text-slate-500">
                Nu ai cont?{' '}
                <Link to="/register" className="font-medium text-brand-600 hover:text-brand-700">
                  Creeaza unul
                </Link>
              </p>
            </form>
          </SectionCard>
        </motion.div>
      </div>
    </PageContainer>
  )
}