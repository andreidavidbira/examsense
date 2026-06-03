/*
ExamSense+ - Frontend Entry Point
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- initializeaza aplicatia React in browser
- configureaza router-ul global al frontend-ului
- inveleste aplicatia cu provider-ele necesare pentru autentificare si notificari
- incarca stilurile globale ale interfetei
*/

import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App'
import { AuthProvider } from './context/AuthContext'
import { ToastProvider } from './context/ToastContext'

// montam aplicatia React in elementul root din pagina HTML
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  </React.StrictMode>
)