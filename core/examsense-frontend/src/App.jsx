/*
ExamSense+ - Main Application Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste componenta principala a aplicatiei React
- deleaga gestionarea navigarii catre router-ul principal
- pastreaza punctul central al frontend-ului simplu si usor de extins
*/

import AppRouter from './router/AppRouter'

// componenta principala a aplicatiei returneaza router-ul global
export default function App() {
  return <AppRouter />
}