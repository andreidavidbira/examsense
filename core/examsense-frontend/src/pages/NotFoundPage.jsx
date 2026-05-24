import { Link } from 'react-router-dom'
import PageContainer from '../components/common/PageContainer'
import SectionCard from '../components/common/SectionCard'

export default function NotFoundPage() {
  return (
    <PageContainer>
      <SectionCard title="Pagina nu a fost găsită" subtitle="Ruta accesată nu există sau a fost mutată.">
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