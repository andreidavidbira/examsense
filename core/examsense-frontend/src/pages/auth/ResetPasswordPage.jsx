import { useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Eye, EyeOff } from 'lucide-react'
import api from '../../api/axios'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import ErrorAlert from '../../components/common/ErrorAlert'
import { useToast } from '../../hooks/useToast'
import { getApiErrorMessages } from '../../utils/errorMessages'
import { primaryButtonClass } from '../../utils/buttonClasses'
import { validateStrongPassword, validatePasswordMatch } from '../../utils/validators'

export default function ResetPasswordPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { showToast } = useToast()

  const uid = useMemo(() => searchParams.get('uid') || '', [searchParams])
  const token = useMemo(() => searchParams.get('token') || '', [searchParams])

  const [form, setForm] = useState({
    new_password: '',
    new_password_confirm: '',
  })
  const [touched, setTouched] = useState({})
  const [message, setMessage] = useState('')
  const [errors, setErrors] = useState([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false)

  const liveErrors = useMemo(() => {
    return {
      new_password: validateStrongPassword(form.new_password),
      new_password_confirm: validatePasswordMatch(form.new_password, form.new_password_confirm),
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
    setMessage('')
    setErrors([])
    setTouched({
      new_password: true,
      new_password_confirm: true,
    })

    if (hasLiveErrors) {
      showToast('Verifică parola nouă înainte de continuare.', 'error')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await api.post('/auth/reset-password/', {
        uid,
        token,
        new_password: form.new_password,
        new_password_confirm: form.new_password_confirm,
      })

      setMessage(response.data.message)
      showToast('Parola a fost resetată cu succes.', 'success')
      navigate('/login')
    } catch (err) {
      const parsedErrors = getApiErrorMessages(err, 'Nu am putut reseta parola.')
      setErrors(parsedErrors)
      showToast('Nu am putut reseta parola.', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <PageContainer>
      <div className="mx-auto max-w-xl py-8 sm:py-12">
        <SectionCard
          title="Setează o parolă nouă"
          subtitle="Introdu noua parolă pentru contul tău."
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Parolă nouă</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="new_password"
                  value={form.new_password}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  autoComplete="new-password"
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3 pr-12 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-800"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {fieldError('new_password') && (
                <p className="mt-2 text-xs text-rose-600">{fieldError('new_password')}</p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Confirmă parola nouă</label>
              <div className="relative">
                <input
                  type={showPasswordConfirm ? 'text' : 'password'}
                  name="new_password_confirm"
                  value={form.new_password_confirm}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  autoComplete="new-password"
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3 pr-12 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                />
                <button
                  type="button"
                  onClick={() => setShowPasswordConfirm((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-800"
                >
                  {showPasswordConfirm ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {fieldError('new_password_confirm') && (
                <p className="mt-2 text-xs text-rose-600">{fieldError('new_password_confirm')}</p>
              )}
            </div>

            {message && (
              <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                {message}
              </div>
            )}

            <ErrorAlert messages={errors} />

            <button disabled={isSubmitting} className={`w-full ${primaryButtonClass}`}>
              {isSubmitting ? 'Se actualizează...' : 'Resetează parola'}
            </button>
          </form>
        </SectionCard>
      </div>
    </PageContainer>
  )
}