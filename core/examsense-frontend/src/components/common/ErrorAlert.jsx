export default function ErrorAlert({ message, messages = [] }) {
  const normalizedMessages = []

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