'use client'

import type { UrgencyLevel } from '@/types'

interface Props {
  daysLeft: string | null
  urgency: UrgencyLevel
  deadline: string | null
}

export function DeadlinePill({ daysLeft, urgency, deadline }: Props) {
  if (!daysLeft && !deadline) return null

  const styles = {
    red: 'bg-red-50 text-red-600',
    yellow: 'bg-amber-50 text-amber-600',
    none: 'bg-gray-50 text-gray-500',
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${styles[urgency]}`}>
      {urgency === 'red' && <span className="mr-1">●</span>}
      {daysLeft || 'No deadline'}
    </span>
  )
}
