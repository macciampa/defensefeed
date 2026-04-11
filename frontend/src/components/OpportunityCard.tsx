'use client'

import type { Opportunity } from '@/types'
import { DeadlinePill } from './DeadlinePill'
import { IntelPanel } from './IntelPanel'
import { MatchBadge } from './MatchBadge'

const SET_ASIDE_LABELS: Record<string, string> = {
  '8AN': '8(a)',
  'SBP': 'Small Business',
  'SDVOSBC': 'SDVOSB',
  'SDVOSBS': 'SDVOSB',
  'WOSB': 'WOSB',
  'HZC': 'HUBZone',
  'HZS': 'HUBZone',
  'VSB': 'Veteran-Owned SB',
  'EDWOSB': 'EDWOSB',
  'TotalSmallBusiness': 'Total Small Business',
  'IEE': 'Indian Economic Enterprise',
}

interface Props {
  opportunity: Opportunity
}

export function OpportunityCard({ opportunity: opp }: Props) {
  const isHighMatch = opp.similarity >= 0.85
  const setAsideLabel = opp.set_aside_type ? (SET_ASIDE_LABELS[opp.set_aside_type] ?? opp.set_aside_type) : null

  const postedDate = opp.posted_date
    ? new Date(opp.posted_date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : null

  const samUrl = `https://sam.gov/opp/${opp.sam_id}/view`

  return (
    <div
      className={[
        'bg-white border transition-all duration-150 group',
        isHighMatch
          ? 'border-l-[3px] border-l-blue-600 border-t-[#e1e4ea] border-r-[#e1e4ea] border-b-[#e1e4ea] rounded-r-lg rounded-tl-none rounded-bl-none'
          : 'border-[#e1e4ea] rounded-lg',
        'hover:shadow-md hover:-translate-y-0.5',
      ].join(' ')}
      style={{ padding: '16px' }}
    >
      {/* Top row: notice type badge + agency + match badge */}
      <div className="flex items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-2 min-w-0">
          {opp.notice_type && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border border-blue-200 text-blue-600 bg-white whitespace-nowrap">
              {opp.notice_type}
            </span>
          )}
          {opp.agency && (
            <span className="text-xs text-gray-500 truncate">{opp.agency}</span>
          )}
        </div>
        <div className="flex-shrink-0">
          <MatchBadge score={opp.score} similarity={opp.similarity} />
        </div>
      </div>

      {/* Title */}
      <h3
        className="font-semibold text-gray-900 mb-2.5 leading-snug"
        style={{
          fontSize: '17px',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}
      >
        {opp.title}
      </h3>

      {/* Tag row */}
      <div className="flex flex-wrap items-center gap-2 mb-3">
        {setAsideLabel && (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
            {setAsideLabel}
          </span>
        )}
        {opp.naics_code && (
          <span
            className="inline-flex items-center px-2 py-0.5 rounded text-xs text-gray-500 bg-gray-50"
            style={{ fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace' }}
          >
            NAICS {opp.naics_code}
          </span>
        )}
      </div>

      {/* Divider */}
      <div className="border-t border-gray-100 mb-3" />

      {/* AI Summary row */}
      {opp.summary && (
        <div className="flex gap-2 mb-3">
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-500 whitespace-nowrap h-fit mt-0.5 flex-shrink-0">
            ✦ AI
          </span>
          <p
            className="text-gray-700"
            style={{ fontSize: '14px', lineHeight: '1.6' }}
          >
            {opp.summary}
          </p>
        </div>
      )}

      {/* Intel panel — lazy fetch on expand */}
      <IntelPanel samId={opp.sam_id} />

      {/* Footer */}
      <div className="flex items-center justify-between gap-3 mt-1">
        <div className="flex items-center gap-3">
          {postedDate && (
            <span className="text-xs text-gray-400">Posted {postedDate}</span>
          )}
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <DeadlinePill
            daysLeft={opp.days_left}
            urgency={opp.urgency}
            deadline={opp.response_deadline}
          />
          <a
            href={samUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-medium text-blue-600 hover:text-blue-700 hover:underline whitespace-nowrap"
          >
            View on SAM.gov →
          </a>
        </div>
      </div>
    </div>
  )
}
