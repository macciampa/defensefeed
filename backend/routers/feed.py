"""
GET /feed — return ranked & scored opportunities for the current user profile.

Scoring uses cosine similarity via pgvector, recency decay, and deadline urgency
as implemented in scoring.py.
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from openai import AsyncOpenAI
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from models import UserProfile
from schemas import FeedResponse, OpportunityOut
from scoring import compute_score, format_days_left, get_urgency_level

router = APIRouter()

# OpportunityOut (from schemas.py) already includes days_left — use it directly.
OpportunityOutFull = OpportunityOut


# ---------------------------------------------------------------------------
# AI summary helper (async)
# ---------------------------------------------------------------------------


async def generate_summary(
    client: AsyncOpenAI,
    title: str,
    description: str | None,
    agency: str | None,
) -> str:
    try:
        desc_snippet = (description or "")[:300]
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Write ONE sentence (max 25 words) summarizing this government contract "
                        "opportunity for a defense contractor. Be specific about what's needed.\n\n"
                        f"Title: {title}\nAgency: {agency}\nDescription: {desc_snippet}"
                    ),
                }
            ],
            max_tokens=60,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return f"Opportunity from {agency or 'government agency'}."


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------


@router.get("/feed", response_model=FeedResponse)
async def get_feed(
    profile_id: int = Query(default=1),
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    profile = db.get(UserProfile, profile_id)
    if profile is None or profile.profile_embedding is None:
        raise HTTPException(status_code=404, detail={"error": "no profile found"})

    # ------------------------------------------------------------------
    # Step 1: Vector search — top 100 candidates by cosine similarity
    # ------------------------------------------------------------------
    profile_vec_str = "[" + ",".join(str(x) for x in profile.profile_embedding) + "]"

    sql = text("""
        SELECT id, sam_id, title, agency, notice_type, naics_code, set_aside_type,
               response_deadline, posted_date, description, synced_at,
               1 - (opportunity_embedding <=> :profile_vec) AS similarity
        FROM opportunities
        WHERE opportunity_embedding IS NOT NULL
        ORDER BY opportunity_embedding <=> :profile_vec
        LIMIT 100
    """)

    rows = db.execute(sql, {"profile_vec": profile_vec_str}).fetchall()

    if not rows:
        return FeedResponse(opportunities=[], total=0)

    # ------------------------------------------------------------------
    # Step 2: Compute full score for each candidate
    # ------------------------------------------------------------------
    scored: list[tuple[float, object, float]] = []
    for row in rows:
        similarity = float(row.similarity)
        posted_date: datetime | None = row.posted_date
        response_deadline: datetime | None = row.response_deadline
        score = compute_score(similarity, posted_date, response_deadline)
        scored.append((score, row, similarity))

    # Sort descending by score, take top `limit`
    scored.sort(key=lambda t: t[0], reverse=True)
    top = scored[:limit]

    # ------------------------------------------------------------------
    # Step 3: Generate AI summaries in parallel
    # ------------------------------------------------------------------
    async_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    summary_tasks = [
        generate_summary(
            async_client,
            title=row.title or "",
            description=row.description,
            agency=row.agency,
        )
        for _, row, _ in top
    ]
    summaries: list[str] = await asyncio.gather(*summary_tasks)

    # ------------------------------------------------------------------
    # Step 4: Build response objects
    # ------------------------------------------------------------------
    results: list[OpportunityOut] = []
    for (score, row, similarity), summary in zip(top, summaries):
        d = {
            "id": row.id,
            "sam_id": row.sam_id,
            "title": row.title,
            "agency": row.agency,
            "notice_type": row.notice_type,
            "naics_code": row.naics_code,
            "set_aside_type": row.set_aside_type,
            "response_deadline": row.response_deadline,
            "posted_date": row.posted_date,
            "description": row.description,
            "synced_at": row.synced_at,
            # Computed fields
            "score": round(score, 4),
            "similarity": round(similarity, 4),
            "urgency": get_urgency_level(row.response_deadline),
            "summary": summary,
            "days_left": format_days_left(row.response_deadline),
        }
        results.append(OpportunityOutFull.model_validate(d))

    return FeedResponse(opportunities=results, total=len(scored))
