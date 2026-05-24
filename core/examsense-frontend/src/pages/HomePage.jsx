import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

import PageContainer from '../components/common/PageContainer'
import SectionCard from '../components/common/SectionCard'
import { useAuth } from '../hooks/useAuth'
import usePageTitle from '../hooks/usePageTitle'

// afisam pagina principala a aplicatiei si adaptam butoanele in functie de autentificare
export default function HomePage() {
  usePageTitle('Acasă')
  const { isAuthenticated } = useAuth()

  return (
    <PageContainer>
      <div className="grid items-center gap-8 py-8 lg:grid-cols-[1.15fr_0.85fr] lg:py-16">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
        >
          <span className="inline-flex rounded-full border border-brand-200 bg-brand-50 px-4 py-1.5 text-sm font-medium text-brand-700">
            Platformă inteligentă pentru învățare și evaluare
          </span>

          <h1 className="mt-6 max-w-4xl text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl lg:text-6xl">
            Învață mai clar. Exersează mai bine. Pregătește-te cu{' '}
            <span className="text-brand-600">ExamSense+</span>.
          </h1>

          <p className="mt-6 max-w-2xl text-base leading-8 text-slate-600 sm:text-lg">
            Încarci cursuri sau materiale, sistemul extrage definiții, generează quiz-uri și îți
            urmărește progresul într-un mod curat, modern și eficient.
          </p>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link
              to={isAuthenticated ? '/documents' : '/register'}
              className="rounded-2xl bg-slate-950 px-6 py-3.5 text-center text-sm font-medium text-white transition hover:opacity-90"
            >
              {isAuthenticated ? 'Intră în aplicație' : 'Creează cont'}
            </Link>

            <Link
              to={isAuthenticated ? '/dashboard' : '/login'}
              className="rounded-2xl border border-slate-200 bg-white px-6 py-3.5 text-center text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            >
              Vezi progresul
            </Link>
          </div>
        </motion.div>

        <SectionCard
          title="Ce poți face"
          subtitle="Un flow complet, de la material brut până la analiză de progres."
        >
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              'Upload documente PDF și DOCX',
              'Extragere definiții în română și engleză',
              'Generare automată de întrebări',
              'Quiz-uri și recapitulare inteligentă',
              'Istoric și scoruri',
              'Dashboard cu puncte slabe',
            ].map((item) => (
              <div
                key={item}
                className="rounded-2xl border border-slate-200/80 bg-slate-50/80 px-4 py-4 text-sm font-medium text-slate-700"
              >
                {item}
              </div>
            ))}
          </div>
        </SectionCard>
      </div>
    </PageContainer>
  )
}