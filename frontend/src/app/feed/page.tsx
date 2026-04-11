'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { getFeed } from '@/lib/api'
import type { Opportunity, ProfileExtraction } from '@/types'
import { OpportunityCard } from '@/components/OpportunityCard'
import { Sidebar } from '@/components/Sidebar'

// ---------------------------------------------------------------------------
// Design tokens / constants
// ---------------------------------------------------------------------------

interface Filters {
  urgency: string
  minMatch: number
  setAsides: {
    eightA: boolean
    sdvosb: boolean
    hubzone: boolean
    totalSB: boolean
  }
}

const SET_ASIDE_CODES: Record<keyof Filters['setAsides'], string[]> = {
  eightA:  ['8AN'],
  sdvosb:  ['SDVOSBC', 'SDVOSBS'],
  hubzone: ['HZC', 'HZS'],
  totalSB: ['TotalSmallBusiness'],
}

// ---------------------------------------------------------------------------
// Skeleton card — shown while loading
// ---------------------------------------------------------------------------

function SkeletonCard() {
  return (
    <div className="bg-white border border-[#e1e4ea] rounded-lg p-4 animate-pulse">
      <div className="flex items-center justify-between mb-3">
        <div className="h-5 bg-gray-100 rounded-full w-24" />
        <div className="h-5 bg-gray-100 rounded-full w-16" />
      </div>
      <div className="h-4 bg-gray-100 rounded w-3/4 mb-2" />
      <div className="h-4 bg-gray-100 rounded w-1/2 mb-4" />
      <div className="border-t border-gray-50 mb-3" />
      <div className="h-3 bg-gray-50 rounded w-full mb-1.5" />
      <div className="h-3 bg-gray-50 rounded w-5/6 mb-4" />
      <div className="flex items-center justify-between">
        <div className="h-3 bg-gray-50 rounded w-20" />
        <div className="h-5 bg-gray-50 rounded-full w-24" />
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Avatar
// ---------------------------------------------------------------------------

function AvatarJD() {
  return (
    <div className="relative">
      <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
        <span className="text-xs font-bold text-white">JD</span>
      </div>
      <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-green-500 border-2 border-white" />
    </div>
  )
}

// ---------------------------------------------------------------------------
// Page root
// ---------------------------------------------------------------------------

export default function FeedPage() {
  const router = useRouter()

  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [profile, setProfile] = useState<ProfileExtraction | null>(null)
  const [filters, setFilters] = useState<Filters>({
    urgency: 'All',
    minMatch: 0,
    setAsides: { eightA: false, sdvosb: false, hubzone: false, totalSB: false },
  })
  // Demo: fixed new-opportunity count banner
  const [newCount] = useState(3)

  // Load profile from sessionStorage (written by /upload after extraction)
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem('defensepulse_profile')
      if (raw) setProfile(JSON.parse(raw) as ProfileExtraction)
    } catch {
      // sessionStorage unavailable — non-fatal
    }
  }, [])

  const fetchFeed = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getFeed(50)
      setOpportunities(data.opportunities)
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to load feed'
      if (msg === 'NO_PROFILE') {
        router.replace('/upload')
        return
      }
      setError(msg)
    } finally {
      setLoading(false)
    }
  }, [router])

  useEffect(() => {
    fetchFeed()
  }, [fetchFeed])

  // Client-side filtering
  const filteredOpportunities = useMemo(() => {
    const activeSetAsides = (Object.keys(filters.setAsides) as Array<keyof typeof filters.setAsides>)
      .filter((k) => filters.setAsides[k])
    return opportunities.filter((opp) => {
      if (opp.similarity < filters.minMatch / 100) return false
      if (filters.urgency === 'Urgent' && opp.urgency !== 'red') return false
      if (filters.urgency === 'Soon' && opp.urgency !== 'red' && opp.urgency !== 'yellow') return false
      if (activeSetAsides.length > 0) {
        const codes = activeSetAsides.flatMap((k) => SET_ASIDE_CODES[k])
        if (!opp.set_aside_type || !codes.includes(opp.set_aside_type)) return false
      }
      return true
    })
  }, [opportunities, filters])

  const matchCount = filteredOpportunities.length

  return (
    <div className="flex h-screen overflow-hidden" style={{ backgroundColor: '#f4f5f7' }}>
      {/* Sidebar */}
      <Sidebar
        matchCount={matchCount}
        profile={profile}
        filters={filters}
        onFiltersChange={setFilters}
      />

      {/* Main content column */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Sticky navbar */}
        <header className="flex-shrink-0 bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="flex items-center justify-between px-6 h-[52px]">
            <div className="flex items-center gap-3">
              <h1 className="text-base font-semibold text-gray-900">Opportunities</h1>
              <span className="text-xs text-gray-400">·</span>
              <span className="text-xs text-gray-400">
                Last synced:{' '}
                <span className="text-gray-500 font-medium">just now</span>
              </span>
            </div>
            <AvatarJD />
          </div>

          {/* New opportunities announcement bar */}
          {newCount > 0 && (
            <div className="flex items-center justify-between px-6 py-1.5 bg-blue-50 border-t border-blue-100">
              <p className="text-xs text-blue-700">
                <span className="mr-1.5">●</span>
                {newCount} new opportunities since your last visit
              </p>
              <button
                onClick={() => fetchFeed()}
                className="text-xs font-medium text-blue-600 hover:text-blue-800 hover:underline"
              >
                Refresh
              </button>
            </div>
          )}
        </header>

        {/* Scrollable feed */}
        <main className="flex-1 overflow-y-auto p-6">
          {/* Loading: skeleton cards */}
          {loading && (
            <div className="space-y-4 max-w-3xl mx-auto">
              {[1, 2, 3, 4].map((i) => (
                <SkeletonCard key={i} />
              ))}
            </div>
          )}

          {/* Error state */}
          {!loading && error && (
            <div className="flex flex-col items-center justify-center py-24 text-center max-w-sm mx-auto">
              <div className="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center mb-4">
                <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
                  <path d="M11 7v6M11 15h.01" stroke="#dc2626" strokeWidth="2" strokeLinecap="round" />
                  <circle cx="11" cy="11" r="9" stroke="#dc2626" strokeWidth="1.5" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-gray-800 mb-1">Failed to load feed</p>
              <p className="text-xs text-gray-500 mb-4">{error}</p>
              <button
                onClick={() => fetchFeed()}
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
              >
                Retry
              </button>
            </div>
          )}

          {/* Empty state */}
          {!loading && !error && filteredOpportunities.length === 0 && (
            <div className="flex flex-col items-center justify-center py-24 text-center max-w-sm mx-auto">
              <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center mb-4">
                <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
                  <circle cx="10" cy="10" r="7" stroke="#9ca3af" strokeWidth="1.5" />
                  <path d="M15.5 15.5l3 3" stroke="#9ca3af" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-gray-700 mb-1">No opportunities found</p>
              <p className="text-xs text-gray-400 leading-relaxed">
                {opportunities.length > 0
                  ? 'Try adjusting your filters or lowering the match threshold.'
                  : 'Try uploading a different capability statement.'}
              </p>
              {opportunities.length === 0 && (
                <a href="/upload" className="mt-4 text-xs font-medium text-blue-600 hover:underline">
                  Upload capability statement →
                </a>
              )}
            </div>
          )}

          {/* Results */}
          {!loading && !error && filteredOpportunities.length > 0 && (
            <div className="max-w-3xl mx-auto">
              {/* Count header */}
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm text-gray-500">
                  Showing{' '}
                  <span className="font-semibold text-gray-800">{filteredOpportunities.length}</span>{' '}
                  {filteredOpportunities.length === 1 ? 'opportunity' : 'opportunities'}
                  {filters.urgency !== 'All' && (
                    <span className="ml-1 text-gray-400">
                      · filtered by &quot;{filters.urgency}&quot;
                    </span>
                  )}
                </p>
                {filters.minMatch > 0 && (
                  <span className="text-xs text-gray-400">Min match: {filters.minMatch}%</span>
                )}
              </div>

              {/* Card list */}
              <div className="space-y-3">
                {filteredOpportunities.map((opp) => (
                  <OpportunityCard key={opp.id} opportunity={opp} />
                ))}
              </div>

              <div className="h-8" />
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

