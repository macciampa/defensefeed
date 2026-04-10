/**
 * Format a deadline ISO string into a human-readable "X days left" label.
 * Returns null if no deadline is provided.
 */
export function format_days_left(deadline: string | null): string | null {
  if (!deadline) return null
  const now = new Date()
  const d = new Date(deadline)
  const diffMs = d.getTime() - now.getTime()
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  if (days < 0) return 'Expired'
  if (days === 0) return 'Due today'
  if (days === 1) return '1 day left'
  return `${days} days left`
}

/**
 * Format a date string to a short human-readable form, e.g. "Apr 15, 2026".
 */
export function formatDate(iso: string | null): string | null {
  if (!iso) return null
  try {
    return new Date(iso).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  } catch {
    return null
  }
}
