/*
ExamSense+ - Page Title Hook
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste hook-ul custom pentru actualizarea titlului paginii
- seteaza un format unitar pentru titlurile din browser
- evita duplicarea logicii de modificare a document.title in paginile aplicatiei
*/

import { useEffect } from 'react'

// actualizam titlul paginii curente in browser
export default function usePageTitle(title) {
  useEffect(() => {
    document.title = title ? `${title} | ExamSense+` : 'ExamSense+'
  }, [title])
}