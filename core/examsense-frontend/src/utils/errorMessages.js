function humanizeFieldName(field) {
  const fieldMap = {
    username: 'Username',
    email: 'Email',
    password: 'Parolă',
    password_confirm: 'Confirmarea parolei',
    old_password: 'Parola veche',
    new_password: 'Parola nouă',
    new_password_confirm: 'Confirmarea noii parole',
    first_name: 'Prenume',
    last_name: 'Nume',
    file: 'Fișier',
    difficulty: 'Dificultate',
    max_questions: 'Numărul de întrebări',
    detail: 'Detalii',
    error: 'Eroare',
  }

  return fieldMap[field] || field.replaceAll('_', ' ')
}

function humanizeMessage(message) {
  if (!message || typeof message !== 'string') {
    return 'Valoare invalidă.'
  }

  const lower = message.toLowerCase()

  if (lower.includes('this field may not be blank')) {
    return 'Câmpul este obligatoriu.'
  }

  if (lower.includes('this field is required')) {
    return 'Câmpul este obligatoriu.'
  }

  if (lower.includes('ensure this field has at least 8 characters')) {
    return 'Trebuie să conțină cel puțin 8 caractere.'
  }

  if (lower.includes('ensure this field has at least 6 characters')) {
    return 'Trebuie să conțină cel puțin 8 caractere.'
  }

  if (lower.includes('enter a valid email address')) {
    return 'Introdu o adresă de email validă.'
  }

  if (lower.includes('unsupported file type')) {
    return 'Tipul de fișier nu este acceptat.'
  }

  if (lower.includes('file is too large')) {
    return 'Fișierul este prea mare.'
  }

  if (lower.includes('token')) {
    return 'Sesiunea a expirat. Te rugăm să te autentifici din nou.'
  }

  return message
}

export function getApiErrorMessages(error, fallback = 'A apărut o eroare neașteptată.') {
  const data = error?.response?.data

  if (!data) {
    return [fallback]
  }

  if (typeof data === 'string') {
    return [humanizeMessage(data)]
  }

  if (data?.detail && typeof data.detail === 'string') {
    return [humanizeMessage(data.detail)]
  }

  if (data?.error && typeof data.error === 'string') {
    return [humanizeMessage(data.error)]
  }

  if (Array.isArray(data)) {
    return data.map((item) => humanizeMessage(String(item)))
  }

  if (typeof data === 'object') {
    const messages = []

    for (const [key, value] of Object.entries(data)) {
      const fieldLabel = humanizeFieldName(key)

      if (Array.isArray(value)) {
        value.forEach((item) => {
          messages.push(`${fieldLabel}: ${humanizeMessage(String(item))}`)
        })
      } else if (typeof value === 'string') {
        messages.push(`${fieldLabel}: ${humanizeMessage(value)}`)
      }
    }

    if (messages.length > 0) {
      return messages
    }
  }

  return [fallback]
}

export function getApiErrorMessage(error, fallback = 'A apărut o eroare neașteptată.') {
  return getApiErrorMessages(error, fallback).join(' ')
}