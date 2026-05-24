export function getDisplayFileName(filePath) {
  if (!filePath) {
    return ''
  }

  const normalized = String(filePath).replaceAll('\\', '/')
  const parts = normalized.split('/')
  return parts[parts.length - 1] || normalized
}