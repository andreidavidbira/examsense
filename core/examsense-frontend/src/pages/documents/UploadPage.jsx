/*
ExamSense+ - Upload Document Page
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste pagina pentru incarcarea documentelor in platforma
- valideaza fisierul si optiunile alese de utilizator
- explica vizual diferentele dintre modurile NLP si AI
- afiseaza un overlay de procesare compatibil cu modul NLP si modul AI
- parcurge vizual toti pasii de procesare inainte de redirectionare
- trimite documentul catre backend pentru procesare si redirectioneaza utilizatorul dupa succes
*/

import { useEffect, useMemo, useRef, useState } from 'react'
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

const uploadHighlights = [
  'Încarci PDF sau DOCX',
  'Alegi generare cu NLP sau AI',
  'Primești definiții și întrebări automat',
  'Poți compara performanța ta cu AI',
]

const processingConfigs = {
  nlp: {
    title: 'Procesare NLP în desfășurare',
    badge: 'Mod NLP',
    description:
      'Aplicația extrage textul, identifică definițiile și construiește întrebări pe baza pipeline-ului NLP.',
    waitMessage:
      'Te rugăm să nu închizi pagina. Pentru documente mari, procesarea NLP poate dura câteva zeci de secunde.',
    steps: [
      {
        title: 'Se extrage textul',
        description: 'Documentul este citit și convertit într-un text analizabil.',
      },
      {
        title: 'Se curăță conținutul',
        description:
          'Sunt eliminate spațiile inutile, artefactele din PDF și fragmentele care pot produce zgomot.',
      },
      {
        title: 'Se identifică definițiile',
        description:
          'Pipeline-ul NLP caută concepte, definiții și formulări relevante în română și engleză.',
      },
      {
        title: 'Se generează întrebările',
        description:
          'Definițiile extrase sunt transformate automat în întrebări pentru quiz.',
      },
      {
        title: 'Se salvează rezultatul',
        description:
          'Documentul, definițiile și întrebările generate sunt salvate în contul tău.',
      },
    ],
  },
  ai: {
    title: 'Generare AI în desfășurare',
    badge: 'Mod AI',
    description:
      'Modelul AI analizează documentul și generează direct definiții și întrebări relevante.',
    waitMessage:
      'Te rugăm să nu închizi pagina. Modul AI poate dura mai mult, mai ales pentru documente mari.',
    steps: [
      {
        title: 'Se extrage textul',
        description: 'Documentul este citit și pregătit pentru analiza automată.',
      },
      {
        title: 'Se pregătește conținutul',
        description:
          'Textul este structurat pentru a putea fi trimis către modulul de generare AI.',
      },
      {
        title: 'AI-ul analizează documentul',
        description:
          'Modelul identifică ideile importante, conceptele și informațiile utile pentru evaluare.',
      },
      {
        title: 'AI-ul generează quiz-ul',
        description:
          'Pe baza materialului, sunt generate definiții și întrebări adaptate dificultății alese.',
      },
      {
        title: 'Se salvează rezultatul',
        description:
          'Documentul și quiz-ul generat sunt salvate pentru a putea fi accesate ulterior.',
      },
    ],
  },
}

// functie simpla folosita pentru animatia finala a overlay-ului
function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function ProcessingOverlay({ currentStep, generationMode }) {
  const config = processingConfigs[generationMode] || processingConfigs.nlp
  const isAiMode = generationMode === 'ai'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/65 px-4 py-6 backdrop-blur-sm">
      <div className="w-full max-w-2xl rounded-[32px] border border-white/20 bg-white p-5 shadow-2xl sm:p-7">
        <div className="mb-6 text-center">
          <div
            className={`mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl ${
              isAiMode
                ? 'bg-violet-50 text-violet-700'
                : 'bg-brand-50 text-brand-700'
            }`}
          >
            <div
              className={`h-8 w-8 animate-spin rounded-full border-4 border-current border-t-transparent ${
                isAiMode ? 'text-violet-700' : 'text-brand-700'
              }`}
            />
          </div>

          <span
            className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${
              isAiMode
                ? 'border-violet-200 bg-violet-50 text-violet-700'
                : 'border-brand-200 bg-brand-50 text-brand-700'
            }`}
          >
            {config.badge}
          </span>

          <h2 className="mt-3 text-2xl font-bold text-slate-950">
            {config.title}
          </h2>

          <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-600">
            {config.description}
          </p>

          <p className="mx-auto mt-2 max-w-xl text-xs leading-5 text-slate-500">
            {config.waitMessage}
          </p>
        </div>

        <div className="space-y-3">
          {config.steps.map((step, index) => {
            const isDone = index < currentStep
            const isActive = index === currentStep

            let containerClass = 'border-slate-200 bg-slate-50'
            let circleClass = 'bg-slate-200 text-slate-500'
            let circleContent = index + 1

            if (isDone) {
              containerClass = 'border-emerald-200 bg-emerald-50'
              circleClass = 'bg-emerald-600 text-white'
              circleContent = '✓'
            }

            if (isActive) {
              containerClass = isAiMode
                ? 'border-violet-200 bg-violet-50'
                : 'border-brand-200 bg-brand-50'

              circleClass = isAiMode
                ? 'bg-violet-600 text-white'
                : 'bg-brand-600 text-white'

              circleContent = (
                <span className="block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              )
            }

            return (
              <div
                key={step.title}
                className={`flex items-start gap-4 rounded-2xl border p-4 transition ${containerClass}`}
              >
                <div
                  className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-sm font-bold ${circleClass}`}
                >
                  {circleContent}
                </div>

                <div className="min-w-0">
                  <p className="font-semibold text-slate-900">{step.title}</p>
                  <p className="mt-1 text-sm leading-6 text-slate-600">
                    {step.description}
                  </p>
                </div>
              </div>
            )
          })}
        </div>

        <p className="mt-5 text-center text-xs text-slate-500">
          După finalizare vei fi redirecționat automat către pagina documentului.
        </p>
      </div>
    </div>
  )
}

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
  const [processingStep, setProcessingStep] = useState(0)

  const processingStepRef = useRef(0)
  const isCompletingAnimationRef = useRef(false)

  const liveErrors = useMemo(() => {
    return {
      file: validateUploadFile(file),
      maxQuestions: validateQuestionCount(maxQuestions),
    }
  }, [file, maxQuestions])

  const hasLiveErrors = Object.values(liveErrors).some(Boolean)

  // pastram pasul curent si intr-un ref pentru animatia de final
  useEffect(() => {
    processingStepRef.current = processingStep
  }, [processingStep])

  // simulam progresul vizual al procesarii fara sa schimbam contractul cu backend-ul
  useEffect(() => {
    if (!isSubmitting) {
      setProcessingStep(0)
      processingStepRef.current = 0
      isCompletingAnimationRef.current = false
      return
    }

    const steps = processingConfigs[generationMode]?.steps || processingConfigs.nlp.steps

    const interval = setInterval(() => {
      setProcessingStep((prev) => {
        // daca request-ul s-a terminat, animatia finala controleaza pasii ramasi
        if (isCompletingAnimationRef.current) {
          return prev
        }

        // ultimul pas ramane rezervat pentru momentul in care backend-ul a terminat
        if (prev >= steps.length - 2) {
          return prev
        }

        return prev + 1
      })
    }, generationMode === 'ai' ? 3200 : 2400)

    return () => clearInterval(interval)
  }, [generationMode, isSubmitting])

  function handleBlur(fieldName) {
    setTouched((prev) => ({
      ...prev,
      [fieldName]: true,
    }))
  }

  // dupa ce backend-ul raspunde, parcurgem vizual pasii ramasi inainte de redirect
  async function finishProcessingAnimation(mode) {
    const steps = processingConfigs[mode]?.steps || processingConfigs.nlp.steps
    const delay = mode === 'ai' ? 700 : 550

    isCompletingAnimationRef.current = true

    const currentStep = processingStepRef.current
    const startStep = Math.min(currentStep + 1, steps.length - 1)

    for (let index = startStep; index < steps.length; index += 1) {
      setProcessingStep(index)
      processingStepRef.current = index
      await wait(delay)
    }

    // lasam ultimul pas vizibil putin, ca utilizatorul sa observe finalizarea
    await wait(500)
  }

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

    const selectedGenerationMode = generationMode

    setProcessingStep(0)
    processingStepRef.current = 0
    isCompletingAnimationRef.current = false
    setIsSubmitting(true)

    try {
      const formData = new FormData()

      formData.append('file', file)
      formData.append('difficulty', difficulty)
      formData.append('generation_mode', selectedGenerationMode)
      formData.append('max_questions', maxQuestions)

      const response = await api.post('/documents/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000,
      })

      await finishProcessingAnimation(selectedGenerationMode)

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
      {isSubmitting && (
        <ProcessingOverlay
          currentStep={processingStep}
          generationMode={generationMode}
        />
      )}

      <div className="grid gap-8 py-8 lg:grid-cols-[0.95fr_1.05fr] lg:py-12">
        <div className="min-w-0">
          <div className="rounded-[30px] border border-brand-100 bg-linear-to-br from-brand-50 via-violet-50 to-white p-6 shadow-sm sm:p-8">
            <span className="inline-flex rounded-full border border-brand-200 bg-white/80 px-4 py-1.5 text-sm font-medium text-brand-700">
              Încarcă un document
            </span>

            <h1 className="mt-5 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
              Transformă rapid materialele tale în definiții, quiz-uri și
              comparații{' '}
              <span className="bg-linear-to-r from-brand-600 via-violet-600 to-cyan-500 bg-clip-text text-transparent">
                User vs AI
              </span>
              .
            </h1>

            <p className="mt-4 max-w-xl text-sm leading-7 text-slate-600 sm:text-base">
              Încarcă un fișier, alege metoda de generare și lasă aplicația să
              construiască un flow complet de învățare și evaluare.
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
                    Modelul citește documentul și generează direct definiții și
                    quiz-uri.
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