import type { FeedResponse, IntelData, ProfileResponse } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function uploadProfile(file: File): Promise<ProfileResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_BASE}/profile`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }))
    throw new Error(err.detail || 'Upload failed')
  }

  return res.json()
}

export async function getFeed(profileId: number, limit = 20): Promise<FeedResponse> {
  const res = await fetch(`${API_BASE}/feed?profile_id=${profileId}&limit=${limit}`)

  if (res.status === 404) {
    throw new Error('NO_PROFILE')
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to load feed' }))
    throw new Error(err.detail || 'Failed to load feed')
  }

  return res.json()
}

export async function getIntel(samId: string, profileId: number): Promise<IntelData> {
  const res = await fetch(`${API_BASE}/intel/${samId}?profile_id=${profileId}`)
  if (!res.ok) {
    throw new Error('intel_unavailable')
  }
  return res.json()
}
