import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import api from '../../api/axios'
import ErrorAlert from '../../components/common/ErrorAlert'
import PageContainer from '../../components/common/PageContainer'
import SectionCard from '../../components/common/SectionCard'
import { useToast } from '../../hooks/useToast'
import usePageTitle from '../../hooks/usePageTitle'
import { primaryButtonClass } from '../../utils/buttonClasses'
import { getApiErrorMessages } from '../../utils/errorMessages'
import {
  validateQuestionCount,
  validateUploadFile,
} from '../../utils/validators'

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

  const liveErrors = useMemo(() => {
    return {
      file: validateUploadFile(file),
      maxQuestions: validateQuestionCount(maxQuestions),
    }
  }, [file, maxQuestions])

  const hasLiveErrors = Object.values(liveErrors).some(Boolean)

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
        timeout: 120000, // 2 minute timeout pentru upload AI
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
      <div className="mx-auto max-w-3xl py-8">
        <SectionCard
          title="Încarcă document"
          subtitle="Adaugă un fișier PDF sau DOCX și generează întrebări cu NLP sau AI."
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

            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-600">
              {generationMode === 'nlp'
                ? 'Mod NLP: documentul este procesat prin pipeline-ul clasic de extragere și generare.'
                : 'Mod AI: modelul citește documentul și generează direct definiții și întrebări.'}
            </div>

            <ErrorAlert messages={errors} />

            <button disabled={isSubmitting} className={primaryButtonClass}>
              {isSubmitting ? 'Se procesează...' : 'Încarcă și procesează'}
            </button>
          </form>
        </SectionCard>
      </div>
    </PageContainer>
  )
}