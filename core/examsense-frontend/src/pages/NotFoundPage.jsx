/*
ExamSense+ - Not Found Page
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste pagina afisata atunci cand utilizatorul acceseaza o ruta inexistenta
- ofera un mesaj clar pentru eroarea de navigare
- permite revenirea rapida catre pagina principala a aplicatiei
*/

import { Link } from 'react-router-dom'

import PageContainer from '../components/common/PageContainer'
import SectionCard from '../components/common/SectionCard'
import usePageTitle from '../hooks/usePageTitle'

// afisam aceasta pagina cand utilizatorul acceseaza o ruta inexistenta
export default function NotFoundPage() {
  usePageTitle('Pagina nu a fost găsită')

  return (
    <PageContainer>
      <SectionCard
        title="Pagina nu a fost găsită"
        subtitle="Ruta accesată nu există sau a fost mutată."
      >
        <div className="flex flex-col items-center gap-4 py-6">
          <p className="text-sm text-slate-500">Verifică adresa sau revino în aplicație.</p>

          <Link
            to="/"
            className="rounded-2xl bg-slate-950 px-5 py-3 text-sm font-medium text-white"
          >
            Înapoi acasă
          </Link>
        </div>
      </SectionCard>
    </PageContainer>
  )
}