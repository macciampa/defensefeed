'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { UploadZone } from '@/components/UploadZone'
import { uploadProfile } from '@/lib/api'
import type { ProfileExtraction } from '@/types'

function ShieldIcon() {
  return (
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M18 2L5 8v9c0 7.455 5.565 14.417 13 16 7.435-1.583 13-8.545 13-16V8L18 2Z"
        fill="#2563eb"
      />
      <path
        d="M12 18l4 4 8-8"
        stroke="white"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function NaicsChip({ code }: { code: string }) {
  return (
    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100">
      {code}
    </span>
  )
}

function CertChip({ cert }: { cert: string }) {
  return (
    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-100">
      {cert}
    </span>
  )
}

function FocusChip({ area }: { area: string }) {
  return (
    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-purple-50 text-purple-700 border border-purple-100">
      {area}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Sample capability statements — static PDFs in /samples/
// ---------------------------------------------------------------------------

const SAMPLES = [
  {
    id: 'tdc',
    file: '/samples/tdc.pdf',
    company: 'TDC',
    industry: 'IT Consulting & Public Safety',
    tags: ['MBE', 'SDB', 'HUB'],
    description: 'Enterprise technology for 911/311, education data, and health exchanges',
  },
  {
    id: 'ztech',
    file: '/samples/ztech.pdf',
    company: 'ZTECH Precision',
    industry: 'Aerospace Manufacturing',
    tags: ['AS9100', 'ITAR', 'CMMC'],
    description: 'Precision CNC machining for aircraft, spacecraft, and armament components',
  },
  {
    id: 'tli',
    file: '/samples/tli.pdf',
    company: 'TLI Construction',
    industry: 'Federal Construction',
    tags: ['8(a)', 'WOSB', 'EDWOSB'],
    description: 'General construction for Air Force, Army, VA, and Coast Guard facilities',
  },
]

export default function UploadPage() {
  const router = useRouter()
  const [uploading, setUploading] = useState(false)
  const [loadingSample, setLoadingSample] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [extraction, setExtraction] = useState<ProfileExtraction | null>(null)

  const handleUpload = async (file: File) => {
    setUploading(true)
    setError(null)
    try {
      const response = await uploadProfile(file)
      setExtraction(response.extraction)
      // Persist the full session (id + extraction) so the feed page can
      // both identify this visitor and populate the sidebar.
      try {
        sessionStorage.setItem(
          'defensepulse_profile',
          JSON.stringify({ id: response.profile_id, extraction: response.extraction }),
        )
      } catch {
        // sessionStorage not available — non-fatal
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Upload failed. Please try again.'
      setError(msg)
      throw err
    } finally {
      setUploading(false)
    }
  }

  const handleSample = async (sample: (typeof SAMPLES)[number]) => {
    setLoadingSample(sample.id)
    setError(null)
    try {
      const res = await fetch(sample.file)
      const blob = await res.blob()
      const file = new File([blob], `${sample.company}.pdf`, { type: 'application/pdf' })
      await handleUpload(file)
    } catch {
      // error already set by handleUpload
    } finally {
      setLoadingSample(null)
    }
  }

  const isBusy = uploading || loadingSample !== null

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center px-4 py-16"
      style={{ backgroundColor: '#f4f5f7' }}
    >
      <div className="w-full max-w-xl">
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-10">
          <ShieldIcon />
          <div className="flex flex-col leading-tight">
            <span className="font-bold text-gray-900 tracking-widest text-lg">DEFENSEPULSE</span>
            <span className="text-xs text-gray-400 tracking-wide">Intelligence Platform</span>
          </div>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl border border-[#e1e4ea] shadow-sm p-8">
          {/* Heading */}
          <div className="text-center mb-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Upload your Capability Statement
            </h1>
            <p className="text-sm text-gray-500 leading-relaxed">
              We'll extract your NAICS codes, certifications, and focus areas to personalize your
              feed.
            </p>
          </div>

          {/* Upload zone */}
          {!extraction && (
            <>
              <UploadZone onUpload={handleUpload} isUploading={uploading} error={error} />

              {/* Sample selector */}
              <div className="mt-8">
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex-1 h-px bg-gray-200" />
                  <span className="text-xs font-medium text-gray-400 uppercase tracking-wide">
                    Or try a sample
                  </span>
                  <div className="flex-1 h-px bg-gray-200" />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {SAMPLES.map((sample) => (
                    <button
                      key={sample.id}
                      onClick={() => handleSample(sample)}
                      disabled={isBusy}
                      className={[
                        'text-left p-3.5 rounded-xl border transition-all duration-150',
                        isBusy
                          ? 'opacity-50 cursor-not-allowed border-gray-200 bg-gray-50'
                          : 'border-gray-200 bg-white hover:border-blue-300 hover:shadow-sm cursor-pointer',
                      ].join(' ')}
                    >
                      <p className="text-sm font-semibold text-gray-900 mb-0.5">
                        {sample.company}
                        {loadingSample === sample.id && (
                          <span className="ml-2 inline-block w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin align-middle" />
                        )}
                      </p>
                      <p className="text-xs text-blue-600 font-medium mb-1.5">{sample.industry}</p>
                      <p className="text-xs text-gray-500 leading-relaxed mb-2">{sample.description}</p>
                      <div className="flex items-center justify-between gap-2 mt-2">
                        <div className="flex flex-wrap gap-1">
                          {sample.tags.map((tag) => (
                            <span
                              key={tag}
                              className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-gray-100 text-gray-500"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                        <a
                          href={sample.file}
                          download={`${sample.company} Capability Statement.pdf`}
                          onClick={(e) => e.stopPropagation()}
                          className="flex-shrink-0 text-gray-400 hover:text-blue-600 transition-colors"
                          title="Download PDF"
                        >
                          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                            <path d="M8 2v8M4 8l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M2 13h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                          </svg>
                        </a>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* Extraction preview */}
          {extraction && (
            <div className="space-y-5">
              {/* Success banner */}
              <div className="flex items-center gap-2.5 p-3 rounded-lg bg-green-50 border border-green-200">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <circle cx="8" cy="8" r="7" fill="#16a34a" />
                  <path d="M5 8l2 2 4-4" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <p className="text-sm font-medium text-green-800">
                  Capability statement analyzed successfully
                  {extraction.company_name ? ` — ${extraction.company_name}` : ''}
                </p>
              </div>

              {/* NAICS codes */}
              {extraction.naics_codes.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                    NAICS Codes Detected
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {extraction.naics_codes.map((code) => (
                      <NaicsChip key={code} code={code} />
                    ))}
                  </div>
                </div>
              )}

              {/* Certifications */}
              {extraction.certifications.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                    Certifications
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {extraction.certifications.map((cert) => (
                      <CertChip key={cert} cert={cert} />
                    ))}
                  </div>
                </div>
              )}

              {/* Focus areas */}
              {extraction.focus_areas.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                    Focus Areas
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {extraction.focus_areas.map((area) => (
                      <FocusChip key={area} area={area} />
                    ))}
                  </div>
                </div>
              )}

              {/* PSC codes (if any) */}
              {extraction.psc_codes.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                    PSC Codes
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {extraction.psc_codes.map((code) => (
                      <span
                        key={code}
                        className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600"
                      >
                        {code}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* CTA */}
              <div className="pt-2">
                <button
                  onClick={() => router.push('/feed')}
                  className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-base transition-colors duration-150 shadow-sm"
                >
                  Load My Feed
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M3 8h10M9 4l4 4-4 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer note */}
        <p className="text-center text-xs text-gray-400 mt-6">
          Your capability statement is processed securely and never shared.
        </p>
      </div>
    </div>
  )
}
