export interface ProfileExtraction {
  naics_codes: string[]
  psc_codes: string[]
  focus_areas: string[]
  certifications: string[]
  keywords: string[]
  company_name: string | null
}

export interface ProfileResponse {
  profile_id: number
  extraction: ProfileExtraction
  uploaded_at: string
}

export type UrgencyLevel = 'red' | 'yellow' | 'none'

export interface Opportunity {
  id: number
  sam_id: string
  title: string
  agency: string | null
  notice_type: string | null
  naics_code: string | null
  set_aside_type: string | null
  response_deadline: string | null
  posted_date: string | null
  description: string | null
  score: number
  similarity: number
  urgency: UrgencyLevel
  summary: string
  days_left: string | null
}

export interface FeedResponse {
  opportunities: Opportunity[]
  total: number
}
