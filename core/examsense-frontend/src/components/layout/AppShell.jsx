/*
ExamSense+ - Application Shell
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste structura comuna de baza a aplicatiei
- afiseaza navbar-ul global pe toate paginile
- randaza continutul fiecarei rute in zona principala a interfetei
*/

import Navbar from './Navbar'

// shell-ul aplicatiei asigura layout-ul comun pentru toate paginile
export default function AppShell({ children }) {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main>{children}</main>
    </div>
  )
}