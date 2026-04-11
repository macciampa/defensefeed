'use client'

import { useState, useCallback } from 'react'
import type { IntelData, IntelIncumbent, IntelPartnerSuggestion, IntelTeamingPair } from '@/types'
import { getIntel } from '@/lib/api'

interface Props {
  samId: string
  profileId: number
}

const CERT_STYLES: Record<string, string> = {
  '8(a)':   'bg-emerald-50 text-emerald-700 border border-emerald-200',
  'SDVOSB': 'bg-blue-50 text-blue-700 border border-blue-200',
  'WOSB':   'bg-orange-50 text-orange-700 border border-orange-200',
  'HUBZone':'bg-purple-50 text-purple-700 border border-purple-200',
}

function formatAmount(n: number): string {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}K`
  return `$${n.toFixed(0)}`
}

// ---- Sub-components --------------------------------------------------------

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5">
      {children}
    </p>
  )
}

function Shimmer() {
  return (
    <div className="animate-pulse space-y-4">
      {/* Incumbents skeleton */}
      <div>
        <div className="h-2.5 bg-gray-200 rounded w-24 mb-2" />
        <div className="h-3.5 bg-gray-200 rounded w-full mb-1.5" />
        <div className="h-3.5 bg-gray-200 rounded w-4/5" />
      </div>
      <div className="border-t border-slate-100" />
      {/* Teaming skeleton */}
      <div>
        <div className="h-2.5 bg-gray-200 rounded w-36 mb-2" />
        <div className="h-3.5 bg-gray-200 rounded w-full mb-1.5" />
        <div className="h-3.5 bg-gray-200 rounded w-3/5" />
      </div>
      <div className="border-t border-slate-100" />
      {/* Partners skeleton */}
      <div>
        <div className="h-2.5 bg-gray-200 rounded w-32 mb-2" />
        <div className="h-3.5 bg-gray-200 rounded w-4/5 mb-1.5" />
        <div className="h-3.5 bg-gray-200 rounded w-full mb-1.5" />
        <div className="h-3.5 bg-gray-200 rounded w-3/5" />
      </div>
    </div>
  )
}

function IncumbentRow({ inc }: { inc: IntelIncumbent }) {
  return (
    <div className="flex items-baseline justify-between gap-2 py-1 border-b border-gray-50 last:border-0">
      <span className="text-[12.5px] font-medium text-gray-800 min-w-0 truncate">{inc.name}</span>
      <div className="flex items-center gap-2 flex-shrink-0">
        <span className="text-[12px] font-semibold text-blue-600 tabular-nums">
          {formatAmount(inc.award_amount)}
        </span>
        {inc.awarded && (
          <span className="text-[11px] text-gray-400 whitespace-nowrap">{inc.awarded}</span>
        )}
      </div>
    </div>
  )
}

function TeamingRow({ pair }: { pair: IntelTeamingPair }) {
  return (
    <div className="py-1 border-b border-gray-50 last:border-0">
      <p className="text-[12.5px] font-medium text-gray-800 leading-snug">
        {pair.prime}{' '}
        <span className="text-gray-400 font-normal">+</span>{' '}
        {pair.sub}
      </p>
      <p className="text-[10.5px] text-gray-400 font-mono mt-0.5">{pair.contract}</p>
    </div>
  )
}

function PartnerRow({ partner }: { partner: IntelPartnerSuggestion }) {
  return (
    <div className="flex items-center justify-between gap-2 py-1 border-b border-gray-50 last:border-0">
      <span className="text-[12.5px] font-medium text-gray-800 min-w-0 truncate">{partner.name}</span>
      {partner.certs.length > 0 && (
        <div className="flex gap-1 flex-shrink-0 flex-wrap justify-end">
          {partner.certs.map((cert) => (
            <span
              key={cert}
              className={`inline-flex items-center px-1.5 py-px rounded-full text-[10px] font-semibold whitespace-nowrap ${
                CERT_STYLES[cert] ?? 'bg-gray-100 text-gray-600 border border-gray-200'
              }`}
            >
              {cert}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}

// ---- Main component --------------------------------------------------------

export function IntelPanel({ samId, profileId }: Props) {
  const [expanded, setExpanded] = useState(false)
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<IntelData | null>(null)
  const [fetchError, setFetchError] = useState(false)

  const handleExpand = useCallback(async () => {
    if (expanded) {
      setExpanded(false)
      return
    }
    setExpanded(true)

    // Already have data — no re-fetch needed
    if (data) return

    setLoading(true)
    setFetchError(false)
    try {
      const result = await getIntel(samId, profileId)
      setData(result)
    } catch {
      setFetchError(true)
    } finally {
      setLoading(false)
    }
  }, [expanded, data, samId, profileId])

  const hasError = fetchError || (data?.error === 'intel_unavailable' || data?.error === 'rate_limited')

  return (
    <>
      {/* Trigger row */}
      <div className="border-t border-gray-100 mt-3 pt-2.5">
        <button
          onClick={handleExpand}
          className="inline-flex items-center gap-1.5 text-[12.5px] font-medium text-gray-500 hover:text-blue-600 transition-colors cursor-pointer select-none"
        >
          <span>🔍</span>
          <span>Who&apos;s involved?</span>
          <span
            className="text-[11px] opacity-60 transition-transform duration-150"
            style={{ transform: expanded ? 'rotate(90deg)' : 'none' }}
          >
            →
          </span>
        </button>
      </div>

      {/* Panel */}
      {expanded && (
        <div className="bg-slate-50 border-t border-slate-200 -mx-4 px-4 pt-3.5 pb-4 mt-2.5 rounded-b-lg">
          {/* Panel header */}
          <div className="flex items-center justify-between mb-3">
            <span className="text-[12.5px] font-semibold text-gray-800">🔍 Who&apos;s involved?</span>
            <button
              onClick={() => setExpanded(false)}
              className="w-5 h-5 flex items-center justify-center rounded text-gray-400 hover:bg-gray-200 hover:text-gray-600 transition-colors text-sm leading-none"
            >
              ×
            </button>
          </div>

          {/* Loading */}
          {loading && <Shimmer />}

          {/* Hard error */}
          {!loading && hasError && (
            <div className="flex items-center justify-between gap-3 px-3 py-2.5 rounded bg-red-50 border border-red-100">
              <span className="text-[12px] text-red-700">
                Intelligence temporarily unavailable — try again.
              </span>
              <button
                onClick={() => { setData(null); setFetchError(false); handleExpand() }}
                className="text-[12px] font-medium text-blue-600 hover:underline flex-shrink-0"
              >
                Retry
              </button>
            </div>
          )}

          {/* Loaded */}
          {!loading && data && !hasError && (
            <>
              {/* INCUMBENTS */}
              <div className="mb-3">
                <SectionLabel>Incumbents</SectionLabel>
                {data.incumbents.length === 0 ? (
                  <div className="flex items-start gap-2 px-2.5 py-2 rounded bg-emerald-50 border border-emerald-100 text-[12px] text-emerald-700 font-medium leading-snug">
                    <span>✦</span>
                    <span>New requirement — no incumbent history found. Lower barrier to entry.</span>
                  </div>
                ) : (
                  data.incumbents.map((inc, i) => <IncumbentRow key={i} inc={inc} />)
                )}
              </div>

              <div className="border-t border-slate-200 mb-3" />

              {/* TEAMING PAIRS */}
              <div className="mb-3">
                <SectionLabel>Known Teaming Pairs</SectionLabel>
                {data.teaming_pairs.length === 0 ? (
                  <p className="text-[12px] text-gray-400 italic">No known teaming pairs found.</p>
                ) : (
                  data.teaming_pairs.map((pair, i) => <TeamingRow key={i} pair={pair} />)
                )}
              </div>

              <div className="border-t border-slate-200 mb-3" />

              {/* SUGGESTED PARTNERS */}
              <div>
                <SectionLabel>
                  Suggested Partners{' '}
                  <span className="normal-case font-normal tracking-normal text-gray-400">
                    (based on your profile + this opportunity&apos;s gaps)
                  </span>
                </SectionLabel>
                {data.partner_suggestions_unavailable ? (
                  <p className="text-[12px] text-gray-400 italic">Partner suggestions unavailable right now.</p>
                ) : data.partner_suggestions.length === 0 ? (
                  <p className="text-[12px] text-gray-400 italic">No partner suggestions found.</p>
                ) : (
                  data.partner_suggestions.map((p, i) => <PartnerRow key={i} partner={p} />)
                )}
              </div>

              {/* Cached timestamp */}
              {data.cached_at && (
                <p className="text-[10.5px] text-gray-400 mt-3 pt-2 border-t border-slate-100">
                  Cached · {new Date(data.cached_at).toLocaleString('en-US', {
                    month: 'short', day: 'numeric', year: 'numeric',
                    hour: 'numeric', minute: '2-digit',
                  })}
                </p>
              )}
            </>
          )}
        </div>
      )}
    </>
  )
}
