interface Props {
  score: number  // 0–1 float from cosine similarity area, displayed as percentage
  similarity: number
}

export function MatchBadge({ similarity }: Props) {
  const pct = Math.round(similarity * 100)

  // High match (≥85%): blue filled; medium (70-84%): blue outline; low: gray
  const style =
    pct >= 85
      ? 'bg-blue-600 text-white'
      : pct >= 70
      ? 'bg-blue-50 text-blue-600 border border-blue-200'
      : 'bg-gray-100 text-gray-600'

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${style}`}>
      {pct}% match
    </span>
  )
}
