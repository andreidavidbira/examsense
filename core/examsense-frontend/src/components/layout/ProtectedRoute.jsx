import { Navigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import LoadingScreen from '../common/LoadingScreen'

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  // cat timp verificam sesiunea, afisam ecranul de loading
  if (isLoading) {
    return <LoadingScreen />
  }

  // daca utilizatorul nu este autentificat, il trimitem la login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}