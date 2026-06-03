/*
ExamSense+ - Forgot Password Page
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste pagina pentru initierea resetarii parolei
- valideaza local adresa de email introdusa
- trimite cererea catre backend pentru generarea linkului de resetare
- afiseaza mesajele de succes sau eroare pentru utilizator
*/

import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import api from '../../api/axios'
import ErrorAlert from '../../components/common/ErrorAlert'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import { useToast } from '../../hooks/useToast'
import usePageTitle from '../../hooks/usePageTitle'
import { primaryButtonClass } from '../../utils/buttonClasses'
import { getApiErrorMessages } from '../../utils/errorMessages'
import { validateEmail } from '../../utils/validators'

// afisam formularul pentru trimiterea emailului de resetare
export default function ForgotPasswordPage() {
  usePageTitle('Resetare parolă')

  const { showToast } = useToast()

  const [email, setEmail] = useState('')
  const [touched, setTouched] = useState(false)
  const [message, setMessage] = useState('')
  const [errors, setErrors] = useState([])
  const [isSubmitting, setIsSubmitting] = useState(false)

  // validam live adresa de email introdusa
  const emailError = useMemo(() => validateEmail(email), [email])

  // trimitem cererea de resetare catre backend
  async function handleSubmit(e) {
    e.preventDefault()
    setTouched(true)
    setMessage('')
    setErrors([])

    if (emailError) {
      showToast('Introdu o adresă de email validă.', 'error')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await api.post('/auth/forgot-password/', { email })
      setMessage(response.data.message)
      showToast('Emailul de resetare a fost procesat.', 'success')
    } catch (err) {
      const parsedErrors = getApiErrorMessages(err, 'Nu am putut procesa cererea.')
      setErrors(parsedErrors)
      showToast('Nu am putut procesa cererea.', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <PageContainer>
      <div className="mx-auto max-w-xl py-8 sm:py-12">
        <SectionCard
          title="Ai uitat parola?"
          subtitle="Introdu adresa de email și vei primi un link pentru resetarea parolei."
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onBlur={() => setTouched(true)}
                autoComplete="email"
                className="w-full rounded-2xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-400 focus:ring-4 focus:ring-brand-100"
                placeholder="nume@email.com"
              />
              {touched && emailError && (
                <p className="mt-2 text-xs text-rose-600">{emailError}</p>
              )}
            </div>

            {message && (
              <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
                {message}
              </div>
            )}

            <ErrorAlert messages={errors} />

            <button disabled={isSubmitting} className={`w-full ${primaryButtonClass}`}>
              {isSubmitting ? 'Se trimite...' : 'Trimite email de resetare'}
            </button>

            <p className="text-center text-sm text-slate-500">
              <Link to="/login" className="font-medium text-brand-600 hover:text-brand-700">
                Înapoi la autentificare
              </Link>
            </p>
          </form>
        </SectionCard>
      </div>
    </PageContainer>
  )
}