/*
ExamSense+ - Page Container Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste containerul principal folosit pentru paginile aplicatiei
- standardizeaza latimea maxima si padding-ul continutului
- mentine consistenta layout-ului intre diferitele ecrane
*/

// incadram continutul paginii intr-un container comun, cu latime si spatiere uniforme
export default function PageContainer({ children }) {
  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8 lg:py-10">
      {children}
    </div>
  )
}