/*
ExamSense+ - Auth Hook
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste hook-ul custom pentru accesarea contextului de autentificare
- ofera componentelor acces simplu la datele si actiunile legate de autentificare
- centralizeaza folosirea AuthContext intr-un singur loc
*/

import { useContext } from 'react'
import { AuthContext } from '../context/AuthContext'

// returnam contextul de autentificare pentru a fi folosit usor in componente
export function useAuth() {
  return useContext(AuthContext)
}