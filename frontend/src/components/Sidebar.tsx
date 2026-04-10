'use client'

import { useState } from 'react'
import type { ProfileExtraction } from '@/types'

interface Filters {
  urgency: string
  minMatch: number
}

interface Props {
  matchCount: number
  profile: ProfileExtraction | null
  filters: Filters
  onFiltersChange: (filters: Filters) => void
}

function ShieldIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M14 2L4 6.5V13.5C4 19.3 8.4 24.74 14 26C19.6 24.74 24 19.3 24 13.5V6.5L14 2Z"
        fill="#2563eb"
      />
      <path
        d="M11 14l2 2 4-4"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function FeedIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="1" y="2" width="14" height="2.5" rx="1" fill="currentColor" />
      <rect x="1" y="6.75" width="14" height="2.5" rx="1" fill="currentColor" />
      <rect x="1" y="11.5" width="9" height="2.5" rx="1" fill="currentColor" />
    </svg>
  )
}

function ProfileIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="8" cy="5" r="3" stroke="currentColor" strokeWidth="1.5" />
      <path d="M2 14c0-3.314 2.686-5 6-5s6 1.686 6 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}

function SettingsIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="8" cy="8" r="2.5" stroke="currentColor" strokeWidth="1.5" />
      <path
        d="M8 1v1.5M8 13.5V15M1 8h1.5M13.5 8H15M2.929 2.929l1.06 1.06M12.01 12.01l1.06 1.06M2.929 13.071l1.06-1.06M12.01 3.99l1.06-1.06"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  )
}

function ChevronIcon({ open }: { open: boolean }) {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 12 12"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={`transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
    >
      <path d="M2 4l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function Sidebar({ matchCount, profile, filters, onFiltersChange }: Props) {
  const [filtersOpen, setFiltersOpen] = useState(true)

  // Set-aside checkboxes — visual only in v1
  const [setAsides, setSetAsides] = useState({
    eightA: false,
    sdvosb: false,
    hubzone: false,
    totalSB: false,
  })

  const urgencyOptions = ['All', 'Urgent', 'Soon']

  return (
    <aside
      className="flex flex-col bg-white border-r border-gray-200 overflow-y-auto overflow-x-hidden flex-shrink-0"
      style={{ width: '240px', minHeight: '100vh' }}
    >
      {/* Brand */}
      <div className="flex items-center gap-2.5 px-4 h-16 border-b border-gray-100 flex-shrink-0">
        <ShieldIcon />
        <div className="flex flex-col leading-tight">
          <span className="font-bold text-gray-900 tracking-widest text-sm">PRYZM</span>
          <span className="text-[10px] text-gray-400 tracking-wide">Intelligence Platform</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="px-3 pt-4 pb-2 space-y-0.5 flex-shrink-0">
        {/* Feed — active */}
        <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-blue-50 text-blue-600 cursor-default">
          <div className="flex items-center gap-2.5 font-semibold text-sm">
            <FeedIcon />
            Feed
          </div>
          {matchCount > 0 && (
            <span className="inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded-full bg-blue-600 text-white text-[10px] font-bold">
              {matchCount > 99 ? '99+' : matchCount}
            </span>
          )}
        </div>

        {/* Profile */}
        <button className="flex items-center gap-2.5 w-full px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 text-sm transition-colors duration-100">
          <ProfileIcon />
          Profile
        </button>

        {/* Settings */}
        <button className="flex items-center gap-2.5 w-full px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 text-sm transition-colors duration-100">
          <SettingsIcon />
          Settings
        </button>
      </nav>

      {/* Divider */}
      <div className="mx-4 border-t border-gray-100 my-2" />

      {/* Filters section */}
      <div className="px-3 flex-shrink-0">
        {/* Collapsible header */}
        <button
          className="flex items-center justify-between w-full px-1 py-2 mb-2"
          onClick={() => setFiltersOpen(!filtersOpen)}
        >
          <span className="text-[10px] font-semibold text-gray-400 tracking-widest uppercase">
            Filters
          </span>
          <ChevronIcon open={filtersOpen} />
        </button>

        {filtersOpen && (
          <div className="space-y-4 pb-2">
            {/* Urgency pills */}
            <div>
              <p className="text-[11px] text-gray-400 mb-1.5 px-1">Urgency</p>
              <div className="flex gap-1.5 flex-wrap">
                {urgencyOptions.map((opt) => (
                  <button
                    key={opt}
                    onClick={() => onFiltersChange({ ...filters, urgency: opt })}
                    className={[
                      'px-2.5 py-1 rounded-full text-xs font-medium transition-colors duration-100',
                      filters.urgency === opt
                        ? opt === 'Urgent'
                          ? 'bg-red-600 text-white'
                          : opt === 'Soon'
                          ? 'bg-amber-500 text-white'
                          : 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
                    ].join(' ')}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>

            {/* Set-aside checkboxes */}
            <div>
              <p className="text-[11px] text-gray-400 mb-1.5 px-1">Set-Aside</p>
              <div className="space-y-1.5">
                {[
                  { key: 'eightA' as const, label: '8(a)' },
                  { key: 'sdvosb' as const, label: 'SDVOSB' },
                  { key: 'hubzone' as const, label: 'HUBZone' },
                  { key: 'totalSB' as const, label: 'Total Small Business' },
                ].map(({ key, label }) => (
                  <label
                    key={key}
                    className="flex items-center gap-2 px-1 cursor-pointer group"
                  >
                    <input
                      type="checkbox"
                      checked={setAsides[key]}
                      onChange={(e) =>
                        setSetAsides((prev) => ({ ...prev, [key]: e.target.checked }))
                      }
                      className="w-3.5 h-3.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-offset-0 cursor-pointer"
                    />
                    <span className="text-xs text-gray-600 group-hover:text-gray-900 select-none">
                      {label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Match threshold slider */}
            <div>
              <div className="flex items-center justify-between px-1 mb-2">
                <p className="text-[11px] text-gray-400">Min Match</p>
                <span className="text-[11px] font-semibold text-blue-600">
                  {filters.minMatch}%
                </span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                step={5}
                value={filters.minMatch}
                onChange={(e) =>
                  onFiltersChange({ ...filters, minMatch: Number(e.target.value) })
                }
                className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(to right, #2563eb ${filters.minMatch}%, #e5e7eb ${filters.minMatch}%)`,
                }}
              />
              <div className="flex justify-between px-0.5 mt-1">
                <span className="text-[10px] text-gray-300">0%</span>
                <span className="text-[10px] text-gray-300">100%</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Divider */}
      <div className="mx-4 border-t border-gray-100" />

      {/* Capability profile card — pinned bottom */}
      <div className="p-3 flex-shrink-0">
        {profile === null ? (
          <div className="rounded-lg border border-dashed border-gray-200 p-3 text-center">
            <p className="text-xs font-medium text-gray-500 mb-1">No capability statement</p>
            <p className="text-[11px] text-gray-400">
              Upload a PDF to personalize your feed
            </p>
            <a
              href="/upload"
              className="inline-block mt-2 text-[11px] font-medium text-blue-600 hover:underline"
            >
              Upload →
            </a>
          </div>
        ) : (
          <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
            {/* Header */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0" />
                <span className="text-xs font-semibold text-gray-700">
                  {profile.company_name ?? 'Capability Statement'}
                </span>
              </div>
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-green-50 text-green-700">
                Active
              </span>
            </div>

            {/* NAICS chips */}
            {profile.naics_codes.length > 0 && (
              <div className="mb-2">
                <p className="text-[10px] text-gray-400 uppercase tracking-wide mb-1">NAICS</p>
                <div className="flex flex-wrap gap-1">
                  {profile.naics_codes.slice(0, 4).map((code) => (
                    <span
                      key={code}
                      className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-50 text-blue-700"
                    >
                      {code}
                    </span>
                  ))}
                  {profile.naics_codes.length > 4 && (
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] text-gray-400">
                      +{profile.naics_codes.length - 4}
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Certs chips */}
            {profile.certifications.length > 0 && (
              <div className="mb-2">
                <p className="text-[10px] text-gray-400 uppercase tracking-wide mb-1">Certs</p>
                <div className="flex flex-wrap gap-1">
                  {profile.certifications.slice(0, 3).map((cert) => (
                    <span
                      key={cert}
                      className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-green-50 text-green-700"
                    >
                      {cert}
                    </span>
                  ))}
                  {profile.certifications.length > 3 && (
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] text-gray-400">
                      +{profile.certifications.length - 3}
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Update link */}
            <a
              href="/upload"
              className="text-[11px] font-medium text-blue-600 hover:underline"
            >
              Update →
            </a>
          </div>
        )}
      </div>
    </aside>
  )
}
