/*
ExamSense+ - Protected Route Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste componenta care protejeaza rutele accesibile doar utilizatorilor autentificati
- verifica starea sesiunii prin contextul de autentificare
- afiseaza un ecran de loading cat timp autentificarea este in curs de verificare
- redirectioneaza utilizatorul spre login daca nu este autentificat
*/

import { Navigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import LoadingScreen from '../common/LoadingScreen'

// permitem accesul la continut doar daca utilizatorul este autentificat
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