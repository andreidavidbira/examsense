/*
ExamSense+ - Upload Document Page
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste pagina pentru incarcarea documentelor in platforma
- valideaza fisierul si optiunile alese de utilizator
- explica vizual diferentele dintre modurile NLP si AI
- trimite documentul catre backend pentru procesare si redirectioneaza utilizatorul dupa succes
*/

import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import api from '../../api/axios'
import ErrorAlert from '../../components/common/ErrorAlert'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import { useToast } from '../../hooks/useToast'
import usePageTitle from '../../hooks/usePageTitle'
import { getApiErrorMessages } from '../../utils/errorMessages'
import {
  validateQuestionCount,
  validateUploadFile,
} from '../../utils/validators'

// mesaje scurte afisate in partea introductiva a paginii
const uploadHighlights = [
  'Încarci PDF sau DOCX',
  'Alegi generare cu NLP sau AI',
  'Primești definiții și întrebări automat',
  'Poți compara performanța ta cu AI',
]

// afisam formularul de upload si gestionam trimiterea documentului spre backend
export default function UploadPage() {
  usePageTitle('Încarcă document')

  const navigate = useNavigate()
  const { showToast } = useToast()

  const [file, setFile] = useState(null)
  const [difficulty, setDifficulty] = useState('medium')
  const [generationMode, setGenerationMode] = useState('nlp')
  const [maxQuestions, setMaxQuestions] = useState(10)
  const [touched, setTouched] = useState({})
  const [errors, setErrors] = useState([])
  const [isSubmitting, setIsSubmitting] = useState(false)

  // validam local campurile importante pentru feedback imediat in UI
  const liveErrors = useMemo(() => {
    return {
      file: validateUploadFile(file),
      maxQuestions: validateQuestionCount(maxQuestions),
    }
  }, [file, maxQuestions])

  const hasLiveErrors = Object.values(liveErrors).some(Boolean)

  // marcam un camp ca fiind atins pentru a afisa erorile doar dupa interactiune
  function handleBlur(fieldName) {
    setTouched((prev) => ({
      ...prev,
      [fieldName]: true,
    }))
  }

  // trimitem documentul catre backend impreuna cu optiunile selectate
  async function handleSubmit(e) {
    e.preventDefault()

    setErrors([])
    setTouched({
      file: true,
      maxQuestions: true,
    })

    if (hasLiveErrors) {
      showToast('Verifică datele înainte de upload.', 'error')
      return
    }

    setIsSubmitting(true)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('difficulty', difficulty)
      formData.append('generation_mode', generationMode)
      formData.append('max_questions', maxQuestions)

      const response = await api.post('/documents/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000,
      })

      showToast('Document încărcat și procesat cu succes.', 'success')
      navigate(`/documents/${response.data.id}`)
    } catch (err) {
      const parsedErrors = getApiErrorMessages(
        err,
        'Upload-ul sau procesarea au eșuat. Verifică fișierul și încearcă din nou.'
      )

      setErrors(parsedErrors)
      showToast('Upload-ul documentului a eșuat.', 'error')
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
              Încarcă un document
            </span>

            <h1 className="mt-5 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
              Transformă rapid materialele tale în definiții, quiz-uri și comparații{' '}
              <span className="bg-linear-to-r from-brand-600 via-violet-600 to-cyan-500 bg-clip-text text-transparent">
                User vs AI
              </span>
              .
            </h1>

            <p className="mt-4 max-w-xl text-sm leading-7 text-slate-600 sm:text-base">
              Încarcă un fișier, alege metoda de generare și lasă aplicația să construiască un flow
              complet de învățare și evaluare.
            </p>

            <div className="mt-6 grid gap-3">
              {uploadHighlights.map((item) => (
                <div
                  key={item}
                  className="rounded-2xl border border-white/70 bg-white/80 px-4 py-3 text-sm font-medium text-slate-700 shadow-xs"
                >
                  {item}
                </div>
              ))}
            </div>

            <div className="mt-6 rounded-[26px] border border-slate-200 bg-white p-4 shadow-xs">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <p className="text-sm font-medium text-slate-500">Mod NLP</p>
                  <p className="mt-2 text-sm leading-7 text-slate-600">
                    Pipeline clasic pentru extragere și generare de întrebări.
                  </p>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <p className="text-sm font-medium text-slate-500">Mod AI</p>
                  <p className="mt-2 text-sm leading-7 text-slate-600">
                    Modelul citește documentul și generează direct definiții și quiz-uri.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <SectionCard
          title="Configurare upload"
          subtitle="Alege fișierul și modul în care vrei să fie procesat."
          className="min-w-0"
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Fișier
              </label>
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                onBlur={() => handleBlur('file')}
                className="block w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm"
              />
              {touched.file && liveErrors.file && (
                <p className="mt-2 text-xs text-rose-600">{liveErrors.file}</p>
              )}
            </div>

            <div className="grid gap-5 sm:grid-cols-3">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Metodă generare
                </label>
                <select
                  value={generationMode}
                  onChange={(e) => setGenerationMode(e.target.value)}
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3"
                >
                  <option value="nlp">NLP</option>
                  <option value="ai">AI</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Dificultate
                </label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3"
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">
                  Număr întrebări
                </label>
                <input
                  type="number"
                  min="1"
                  max="30"
                  value={maxQuestions}
                  onChange={(e) => setMaxQuestions(e.target.value)}
                  onBlur={() => handleBlur('maxQuestions')}
                  className="w-full rounded-2xl border border-slate-200 px-4 py-3"
                />
                {touched.maxQuestions && liveErrors.maxQuestions && (
                  <p className="mt-2 text-xs text-rose-600">
                    {liveErrors.maxQuestions}
                  </p>
                )}
              </div>
            </div>

            {/* afisam o explicatie scurta pentru metoda selectata */}
            <div
              className={`rounded-3xl border px-4 py-4 text-sm ${
                generationMode === 'nlp'
                  ? 'border-brand-200 bg-brand-50 text-brand-700'
                  : 'border-violet-200 bg-violet-50 text-violet-700'
              }`}
            >
              {generationMode === 'nlp'
                ? 'Ai ales modul NLP: documentul va fi procesat prin pipeline-ul clasic de extragere și generare.'
                : 'Ai ales modul AI: modelul va analiza documentul și va genera direct definiții și întrebări.'}
            </div>

            <ErrorAlert messages={errors} />

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full rounded-2xl bg-slate-950 px-6 py-3.5 text-sm font-medium text-white transition hover:opacity-95 disabled:opacity-70"
            >
              {isSubmitting ? 'Se procesează...' : 'Încarcă și procesează'}
            </button>
          </form>
        </SectionCard>
      </div>
    </PageContainer>
  )
}