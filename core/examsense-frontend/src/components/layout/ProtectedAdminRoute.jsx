import { Navigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import PageLoader from '../common/PageLoader'

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