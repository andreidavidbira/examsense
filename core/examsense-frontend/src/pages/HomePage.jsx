import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

import PageContainer from '../components/common/PageContainer'
import SectionCard from '../components/common/SectionCard'
import { useAuth } from '../hooks/useAuth'
import usePageTitle from '../hooks/usePageTitle'

const features = [
  {
    title: 'Upload rapid',
    description: 'Încarci documente PDF și DOCX direct în platformă.',
  },
  {
    title: 'Definiții extrase',
    description: 'Sistemul identifică noțiunile importante pentru învățare.',
  },
  {
    title: 'Quiz NLP sau AI',
    description: 'Poți genera întrebări automat prin două abordări diferite.',
  },
  {
    title: 'Comparație user vs AI',
    description: 'Vezi cum te descurci față de un solver AI pe același quiz.',
  },
]

const stats = [
  { label: 'Moduri generare', value: 'NLP + AI' },
  { label: 'Comparație', value: 'User vs AI' },
  { label: 'Fișiere acceptate', value: 'PDF / DOCX' },
]

export default function HomePage() {
  usePageTitle('Acasă')
  const { isAuthenticated } = useAuth()

  return (
    <PageContainer>
      <div className="space-y-8 py-8 sm:space-y-10 lg:space-y-12 lg:py-12">
        <section className="grid items-center gap-8 lg:grid-cols-[1.15fr_0.85fr]">
          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45 }}
            className="min-w-0"
          >
            <span className="inline-flex rounded-full border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700 shadow-xs">
              Platformă inteligentă pentru învățare și evaluare
            </span>

            <h1 className="mt-6 max-w-4xl text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl lg:text-6xl">
              Transformă documentele în quiz-uri inteligente și învață mai eficient cu{' '}
              <span className="relative inline-block">
                <span className="absolute inset-0 rounded-xl bg-linear-to-r from-brand-300/30 via-violet-300/30 to-cyan-300/30 blur-xl" />
                <span className="relative bg-linear-to-r from-brand-600 via-violet-600 to-cyan-500 bg-clip-text text-transparent drop-shadow-[0_0_10px_rgba(99,102,241,0.25)]">
                  ExamSense+
                </span>
              </span>
              .
            </h1>

            <p className="mt-6 max-w-2xl text-base leading-8 text-slate-600 sm:text-lg">
              Încarci materiale de studiu, aplicația extrage concepte importante, generează
              întrebări automat și îți oferă o imagine clară asupra progresului tău, inclusiv
              comparații directe între performanța utilizatorului și a unui solver AI.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link
                to={isAuthenticated ? '/documents' : '/register'}
                className="rounded-2xl bg-slate-950 px-6 py-3.5 text-center text-sm font-medium text-white shadow-sm transition hover:-translate-y-0.5 hover:opacity-95"
              >
                {isAuthenticated ? 'Intră în aplicație' : 'Creează cont'}
              </Link>

              <Link
                to={isAuthenticated ? '/dashboard' : '/login'}
                className="rounded-2xl border border-slate-200 bg-white px-6 py-3.5 text-center text-sm font-medium text-slate-700 shadow-sm transition hover:-translate-y-0.5 hover:bg-slate-50"
              >
                {isAuthenticated ? 'Vezi dashboard-ul' : 'Autentificare'}
              </Link>
            </div>

            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              {stats.map((item) => (
                <div
                  key={item.label}
                  className="rounded-2xl border border-slate-200/80 bg-white/90 px-4 py-4 shadow-xs"
                >
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    {item.label}
                  </p>
                  <p className="mt-2 text-sm font-semibold text-slate-900">{item.value}</p>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.08 }}
            className="min-w-0"
          >
            <div className="relative overflow-hidden rounded-4xl border border-slate-200 bg-linear-to-br from-white via-slate-50 to-brand-50/50 p-5 shadow-sm sm:p-6">
              <div className="absolute -right-12 -top-12 h-32 w-32 rounded-full bg-brand-200/30 blur-3xl" />
              <div className="absolute -bottom-10 -left-10 h-28 w-28 rounded-full bg-violet-200/30 blur-3xl" />

              <div className="relative space-y-4">
                <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-xs">
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-slate-900">Document încărcat</p>
                      <p className="mt-1 truncate text-xs text-slate-500">
                        materie_examen_licenta.pdf
                      </p>
                    </div>

                    <span className="shrink-0 rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
                      Procesat
                    </span>
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-xs">
                    <p className="text-sm font-medium text-slate-500">Generare quiz</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
                        NLP
                      </span>
                      <span className="rounded-full bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700">
                        AI
                      </span>
                    </div>
                    <p className="mt-3 text-xs text-slate-500">
                      Alegi metoda de generare direct la creare.
                    </p>
                  </div>

                  <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-xs">
                    <p className="text-sm font-medium text-slate-500">Quiz finalizat</p>
                    <p className="mt-3 text-2xl font-semibold tracking-tight text-slate-950">
                      10 întrebări
                    </p>
                    <p className="mt-2 text-xs text-slate-500">
                      Timp, răspunsuri și comparație salvate în istoric.
                    </p>
                  </div>
                </div>

                <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-xs">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-900">User vs AI</p>
                      <p className="mt-1 text-xs text-slate-500">
                        Compari performanța utilizatorului cu solverul AI.
                      </p>
                    </div>

                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      Același quiz
                    </span>
                  </div>

                  <div className="mt-4 grid gap-3 sm:grid-cols-2">
                    <div className="rounded-2xl border border-brand-200 bg-brand-50/70 p-3">
                      <p className="text-xs font-medium uppercase tracking-wide text-brand-700">
                        User
                      </p>
                      <p className="mt-2 text-lg font-semibold text-slate-950">8 / 10</p>
                      <p className="mt-1 text-xs text-slate-500">Timp: 3m 24s</p>
                    </div>

                    <div className="rounded-2xl border border-violet-200 bg-violet-50/70 p-3">
                      <p className="text-xs font-medium uppercase tracking-wide text-violet-700">
                        AI
                      </p>
                      <p className="mt-2 text-lg font-semibold text-slate-950">7 / 10</p>
                      <p className="mt-1 text-xs text-slate-500">Timp: 12s</p>
                    </div>
                  </div>

                  <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">
                    <div className="h-full w-[80%] rounded-full bg-linear-to-r from-brand-500 to-violet-500" />
                  </div>

                  <p className="mt-3 text-xs text-slate-500">
                    Sistemul păstrează scorul, timpul și răspunsurile pentru ambele părți.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </section>

        <SectionCard
          title="Ce poți face cu ExamSense+"
          subtitle="Un flow complet, de la material brut până la analiză de progres."
        >
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {features.map((item, index) => (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, delay: 0.08 * index }}
                className="rounded-3xl border border-slate-200/80 bg-linear-to-br from-white to-slate-50/80 p-5 shadow-xs transition hover:-translate-y-0.5 hover:shadow-sm"
              >
                <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-50 text-sm font-semibold text-brand-700">
                  {index + 1}
                </div>

                <h3 className="text-base font-semibold text-slate-950">{item.title}</h3>
                <p className="mt-3 text-sm leading-7 text-slate-600">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </SectionCard>
      </div>
    </PageContainer>
  )
}