/*
ExamSense+ - Toast Hook
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste hook-ul custom pentru accesarea contextului de toast
- ofera componentelor o metoda simpla de folosire a notificarilor globale
- centralizeaza accesul la ToastContext intr-un singur loc
*/

import { useContext } from 'react'
import { ToastContext } from '../context/ToastContext'

// returnam contextul de toast pentru a putea afisa notificari din orice componenta
export function useToast() {
  return useContext(ToastContext)
}