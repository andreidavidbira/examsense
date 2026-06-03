/*
ExamSense+ - Error Alert Component
Copyright (c) Bîra Andrei-David.
Acest fisier face parte din proiectul ExamSense+.

Rolul fisierului:
- defineste componenta reutilizabila pentru afisarea mesajelor de eroare
- accepta fie un singur mesaj, fie o lista de mesaje
- normalizeaza si afiseaza erorile intr-un format vizual unitar
*/

export default function ErrorAlert({ message, messages = [] }) {
  const normalizedMessages = []

  // normalizam intr-o singura lista mesajele primite prin props
  if (Array.isArray(messages) && messages.length > 0) {
    normalizedMessages.push(...messages.filter(Boolean))
  } else if (message) {
    normalizedMessages.push(message)
  }

  if (normalizedMessages.length === 0) {
    return null
  }

  return (
    <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
      {normalizedMessages.length === 1 ? (
        <p>{normalizedMessages[0]}</p>
      ) : (
        <ul className="space-y-1">
          {normalizedMessages.map((item, index) => (
            <li key={`${item}-${index}`} className="leading-6">
              • {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}