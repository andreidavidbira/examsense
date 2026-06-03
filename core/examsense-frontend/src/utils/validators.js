/*
ExamSense+ - Frontend Validation Helpers
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste functiile de validare folosite in formularele din frontend
- verifica datele introduse de utilizator inainte de trimiterea lor catre backend
- centralizeaza regulile de validare pentru email, username, parola, upload si quiz-uri
*/

// validam formatul de baza pentru email
export function validateEmail(email) {
  if (!email || !email.trim()) {
    return 'Emailul este obligatoriu.'
  }

  if (!email.includes('@')) {
    return 'Emailul trebuie să conțină caracterul @.'
  }

  return ''
}

// verificam daca parola respecta regulile minime de siguranta
export function validateStrongPassword(password) {
  if (!password) return 'Parola este obligatorie.'
  if (password.length < 8) return 'Parola trebuie să aibă minim 8 caractere.'

  const hasUpper = /[A-Z]/.test(password)
  const hasLower = /[a-z]/.test(password)
  const hasDigit = /\d/.test(password)

  if (!hasUpper || !hasLower || !hasDigit) {
    return 'Parola ar trebui să conțină literă mare, literă mică și cifră.'
  }

  return ''
}

// verificam daca cele doua parole introduse coincid
export function validatePasswordMatch(password, confirmPassword) {
  if (!confirmPassword) return 'Confirmarea parolei este obligatorie.'
  if (password !== confirmPassword) return 'Parolele nu coincid.'
  return ''
}

// validam username-ul introdus de utilizator
export function validateUsername(username) {
  if (!username || !username.trim()) {
    return 'Username-ul este obligatoriu.'
  }

  if (username.trim().length < 3) {
    return 'Username-ul trebuie să aibă minim 3 caractere.'
  }

  return ''
}

// validam generic un camp text obligatoriu
export function validateRequiredText(value, label = 'Câmpul') {
  if (!value || !value.trim()) {
    return `${label} este obligatoriu.`
  }

  return ''
}

// validam fisierul ales pentru upload
export function validateUploadFile(file) {
  if (!file) {
    return 'Selectează un fișier PDF sau DOCX.'
  }

  const name = file.name?.toLowerCase() || ''

  if (!name.endsWith('.pdf') && !name.endsWith('.docx')) {
    return 'Sunt acceptate doar fișiere PDF sau DOCX.'
  }

  return ''
}

// validam numarul de intrebari cerut la generarea quiz-ului
export function validateQuestionCount(value) {
  const numericValue = Number(value)

  if (!numericValue) {
    return 'Numărul de întrebări este obligatoriu.'
  }

  if (numericValue < 1) {
    return 'Numărul minim de întrebări este 1.'
  }

  if (numericValue > 30) {
    return 'Numărul maxim de întrebări este 30.'
  }

  return ''
}