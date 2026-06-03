/*
ExamSense+ - Vite Frontend Configuration
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- configureaza mediul de development pentru frontend-ul aplicatiei
- activeaza suportul pentru React si Tailwind CSS prin Vite
- stabileste portul local folosit la rularea interfetei
*/

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// definim configuratia principala pentru frontend-ul Vite
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // portul local folosit de frontend in development
    port: 5173,
  },
})