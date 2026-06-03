/*
ExamSense+ - Profile Page
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste pagina de profil a utilizatorului
- afiseaza si permite editarea datelor principale ale contului
- valideaza local campurile importante din formular
- trimite modificarile catre backend si actualizeaza profilul din context
*/

import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import api from '../../api/axios'
import ErrorAlert from '../../components/common/ErrorAlert'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import { useAuth } from '../../hooks/useAuth'
import { useToast } from '../../hooks/useToast'
import usePageTitle from '../../hooks/usePageTitle'
import {
  primaryButtonClass,
  secondaryButtonClass,
} from '../../utils/buttonClasses'
import { getApiErrorMessages } from '../../utils/errorMessages'
import {
  validateEmail,
  validateRequiredText,
  validateUsername,
} from '../../utils/validators'

// afisam pagina de profil si permitem actualizarea datelor de baza ale utilizatorului
export default function ProfilePage() {
  usePageTitle('Profilul meu')

  const { user, refreshProfile } = useAuth()
  const { showToast } = useToast()

  const [form, setForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
  })

  const [touched, setTouched] = useState({})
  const [message, setMessage] = useState('')
  const [errors, setErrors] = useState([])
  const [isSubmitting, setIsSubmitting] = useState(false)

  // cand primim datele utilizatorului, le copiem in formular
  useEffect(() => {
    if (user) {
      setForm({
        username: user.username || '',
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
      })
    }
  }, [user])

  // validam live campurile principale ale profilului
  const liveErrors = useMemo(() => {
    return {
      username: validateUsername(form.username),
      email: validateEmail(form.email),
      first_name: validateRequiredText(form.first_name, 'Prenumele'),
      last_name: validateRequiredText(form.last_name, 'Numele'),
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

  // trimitem modificarile catre backend si reincarcam profilul din context
  async function handleSubmit(e) {
    e.preventDefault()
    setMessage('')
    setErrors([])
    setTouched({
      username: true,
      email: true,
      first_name: true,
      last_name: true,
    })

    if (hasLiveErrors) {
      showToast('Verifică datele introduse înainte de salvare.', 'error')
      return
    }

    setIsSubmitting(true)

    try {
      await api.put('/auth/profile/', form)
      await refreshProfile()

      setMessage('Profil actualizat cu succes.')
      showToast('Profil actualizat cu succes.', 'success')
    } catch (err) {
      const parsedErrors = getApiErrorMessages(
        err,
        'Actualizarea profilului a eșuat.'
      )
      setErrors(parsedErrors)
      showToast('Actualizarea profilului a eșuat.', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <PageContainer>
      <div className="mx-auto max-w-3xl py-8">
        <SectionCard
          title="Profilul meu"
          subtitle="Gestionează informațiile contului tău și păstrează datele actualizate."
        >
          <form onSubmit={handleSubmit} className="grid gap-5 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Username
              </label>
              <input
                name="username"
                value={form.username}
                onChange={handleChange}
                onBlur={handleBlur}
                autoComplete="username"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                placeholder="Username-ul tău"
              />
              {fieldError('username') && (
                <p className="mt-2 text-xs text-rose-600">{fieldError('username')}</p>
              )}
            </div>

            <div className="sm:col-span-2">
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Email
              </label>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                onBlur={handleBlur}
                autoComplete="email"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                placeholder="Adresa ta de email"
              />
              {fieldError('email') && (
                <p className="mt-2 text-xs text-rose-600">{fieldError('email')}</p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Prenume
              </label>
              <input
                name="first_name"
                value={form.first_name}
                onChange={handleChange}
                onBlur={handleBlur}
                autoComplete="given-name"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                placeholder="Prenume"
              />
              {fieldError('first_name') && (
                <p className="mt-2 text-xs text-rose-600">{fieldError('first_name')}</p>
              )}
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Nume
              </label>
              <input
                name="last_name"
                value={form.last_name}
                onChange={handleChange}
                onBlur={handleBlur}
                autoComplete="family-name"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                placeholder="Nume"
              />
              {fieldError('last_name') && (
                <p className="mt-2 text-xs text-rose-600">{fieldError('last_name')}</p>
              )}
            </div>

            {message && (
              <div className="sm:col-span-2 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                {message}
              </div>
            )}

            <div className="sm:col-span-2">
              <ErrorAlert messages={errors} />
            </div>

            <div className="sm:col-span-2 flex flex-col gap-3 sm:flex-row">
              <button
                type="submit"
                disabled={isSubmitting}
                className={`w-full sm:w-auto ${primaryButtonClass}`}
              >
                {isSubmitting ? 'Se salvează...' : 'Salvează modificările'}
              </button>

              <Link
                to="/change-password"
                className={`inline-flex w-full items-center justify-center sm:w-auto ${secondaryButtonClass}`}
              >
                Schimbă parola
              </Link>
            </div>
          </form>
        </SectionCard>
      </div>
    </PageContainer>
  )
}