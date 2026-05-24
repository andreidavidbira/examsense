import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Eye, EyeOff } from 'lucide-react'
import api from '../../api/axios'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import ErrorAlert from '../../components/common/ErrorAlert'
import { getApiErrorMessages } from '../../utils/errorMessages'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../hooks/useToast'
import { primaryButtonClass } from '../../utils/buttonClasses'
import {
  validateRequiredText,
  validateStrongPassword,
  validatePasswordMatch,
} from '../../utils/validators'

export default function ChangePasswordPage() {
  const navigate = useNavigate()
  const { logout } = useAuth()
  const { showToast } = useToast()

  const [form, setForm] = useState({
    old_password: '',
    new_password: '',
    new_password_confirm: '',
  })
  const [touched, setTouched] = useState({})
  const [message, setMessage] = useState('')
  const [errors, setErrors] = useState([])
  const [isSubmitting, setIsSubmitting] = useState(false)

  const [showOldPassword, setShowOldPassword] = useState(false)
  const [showNewPassword, setShowNewPassword] = useState(false)
  const [showNewPasswordConfirm, setShowNewPasswordConfirm] = useState(false)

  const liveErrors = useMemo(() => {
    return {
      old_password: validateRequiredText(form.old_password, 'Parola veche'),
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
      old_password: true,
      new_password: true,
      new_password_confirm: true,
    })

    if (hasLiveErrors) {
      showToast('Verifică datele introduse înainte de schimbarea parolei.', 'error')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await api.post('/auth/change-password/', form)
      setMessage(response.data.message || 'Parola a fost schimbată cu succes.')
      showToast('Parola a fost schimbată.', 'success')

      setForm({
        old_password: '',
        new_password: '',
        new_password_confirm: '',
      })

      if (response.data.logout_required) {
        await logout()
        navigate('/login')
      }
    } catch (err) {
      const parsedErrors = getApiErrorMessages(err, 'Nu am putut schimba parola.')
      setErrors(parsedErrors)
      showToast('Nu am putut schimba parola.', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <PageContainer>
      <div className="mx-auto max-w-2xl py-8">
        <SectionCard
          title="Schimbare parolă"
          subtitle="Alege o parolă nouă, sigură și ușor de reținut pentru tine."
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Parola veche</label>
              <div className="relative">
                <input
                  type={showOldPassword ? 'text' : 'password'}
                  name="old_password"
                  value={form.old_password}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  autoComplete="current-password"
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3 pr-12 outline-none focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                />
                <button
                  type="button"
                  onClick={() => setShowOldPassword((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-800"
                >
                  {showOldPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {fieldError('old_password') && (
                <p className="mt-2 text-xs text-rose-600">{fieldError('old_password')}</p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Parola nouă</label>
              <div className="relative">
                <input
                  type={showNewPassword ? 'text' : 'password'}
                  name="new_password"
                  value={form.new_password}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  autoComplete="new-password"
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3 pr-12 outline-none focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPassword((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-800"
                >
                  {showNewPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {fieldError('new_password') ? (
                <p className="mt-2 text-xs text-rose-600">{fieldError('new_password')}</p>
              ) : (
                <p className="mt-2 text-xs text-slate-500">
                  Folosește minim 8 caractere și o combinație cât mai puternică.
                </p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">Confirmă parola nouă</label>
              <div className="relative">
                <input
                  type={showNewPasswordConfirm ? 'text' : 'password'}
                  name="new_password_confirm"
                  value={form.new_password_confirm}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  autoComplete="new-password"
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3 pr-12 outline-none focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPasswordConfirm((prev) => !prev)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-800"
                >
                  {showNewPasswordConfirm ? <EyeOff size={18} /> : <Eye size={18} />}
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

            <button disabled={isSubmitting} className={primaryButtonClass}>
              {isSubmitting ? 'Se actualizează...' : 'Schimbă parola'}
            </button>
          </form>
        </SectionCard>
      </div>
    </PageContainer>
  )
}