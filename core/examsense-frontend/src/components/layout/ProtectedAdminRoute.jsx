/*
ExamSense+ - Protected Admin Route Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste componenta care protejeaza rutele accesibile doar administratorilor
- verifica autentificarea si rolul utilizatorului prin contextul de autentificare
- afiseaza un loader cat timp sesiunea este in curs de verificare
- redirectioneaza utilizatorii neautorizati catre zonele potrivite ale aplicatiei
*/

import { Navigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import PageLoader from '../common/PageLoader'

// permitem accesul doar utilizatorilor autentificati care au rol de administrator
export default function ProtectedAdminRoute({ children }) {
  const { user, isAuthenticated, isLoading } = useAuth()

  // cat timp verificam sesiunea, afisam loaderul
  if (isLoading) {
    return <PageLoader text="Se verifică accesul de administrator..." />
  }

  // daca utilizatorul nu este autentificat, il trimitem la login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // daca utilizatorul nu este admin, il redirectionam catre zona normala a aplicatiei
  if (!user?.is_staff) {
    return <Navigate to="/documents" replace />
  }

  return children
}