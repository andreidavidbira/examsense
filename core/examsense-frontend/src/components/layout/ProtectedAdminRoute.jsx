import { Navigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import PageLoader from '../common/PageLoader'

export default function ProtectedAdminRoute({ children }) {
  const { user, isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <PageLoader text="Se verifică accesul de administrator..." />
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (!user?.is_staff) {
    return <Navigate to="/documents" replace />
  }

  return children
}