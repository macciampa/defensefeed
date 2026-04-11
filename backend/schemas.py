from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ProfileExtraction(BaseModel):
    naics_codes: list[str] = []
    psc_codes: list[str] = []
    focus_areas: list[str] = []
    certifications: list[str] = []
    keywords: list[str] = []
    company_name: str | None = None


class ProfileResponse(BaseModel):
    profile_id: int
    extraction: ProfileExtraction
    uploaded_at: str


class OpportunityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sam_id: str
    title: str | None = None
    agency: str | None = None
    notice_type: str | None = None
    naics_code: str | None = None
    set_aside_type: str | None = None
    response_deadline: datetime | None = None
    posted_date: datetime | None = None
    description: str | None = None
    synced_at: datetime | None = None
    sam_link: str | None = None

    # Computed / scored fields — not stored in the ORM row
    score: float = 0.0
    similarity: float = 0.0
    urgency: Literal["red", "yellow", "none"] = "none"
    summary: str = ""
    days_left: str | None = None


class FeedResponse(BaseModel):
    opportunities: list[OpportunityOut]
    total: int


# ---------------------------------------------------------------------------
# Intel endpoint schemas  (GET /intel/{sam_id})
# ---------------------------------------------------------------------------

class IncumbentOut(BaseModel):
    name: str
    award_amount: float
    awarded: str


class TeamingPairOut(BaseModel):
    prime: str
    sub: str
    contract: str


class PartnerSuggestionOut(BaseModel):
    name: str
    naics: str
    certs: list[str]


class IntelResponse(BaseModel):
    incumbents: list[IncumbentOut] = []
    teaming_pairs: list[TeamingPairOut] = []
    partner_suggestions: list[PartnerSuggestionOut] = []
    cached_at: str | None = None
    partner_suggestions_unavailable: bool = False
    error: str | None = None  # "intel_unavailable" | "rate_limited"
