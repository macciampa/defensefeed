"""
GET /intel/{sam_id} — People Intelligence Layer.

Returns incumbents, known teaming pairs, and partner suggestions for an
opportunity. Lazy-fetched on first card expand, cached in DB for 7 days.

Data sources:
  - USASpending.gov (free, no key): prime awards + subawards
  - SAM.gov entity search (existing SAM_API_KEY): partner suggestions

Timeout budget: 12s total for USASpending chain, 8s for SAM.gov.
Always returns valid JSON — never raises an exception to the caller.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    IncumbentOut,
    IntelResponse,
    PartnerSuggestionOut,
    TeamingPairOut,
)

logger = logging.getLogger(__name__)
router = APIRouter()

SAM_API_KEY = os.getenv("SAM_API_KEY", "")

# ---------------------------------------------------------------------------
# Agency name normalization
# SAM.gov stores fullParentPathName like "DEPT OF DEFENSE:DARPA".
# Split on ":", take first segment, map to USASpending title-case name.
# ---------------------------------------------------------------------------
_AGENCY_MAP: dict[str, str] = {
    "DEPT OF DEFENSE": "Department of Defense",
    "DEPARTMENT OF DEFENSE": "Department of Defense",
    "DOD": "Department of Defense",
    "DEPT OF THE AIR FORCE": "Department of the Air Force",
    "DEPARTMENT OF THE AIR FORCE": "Department of the Air Force",
    "DEPT OF THE ARMY": "Department of the Army",
    "DEPARTMENT OF THE ARMY": "Department of the Army",
    "DEPT OF THE NAVY": "Department of the Navy",
    "DEPARTMENT OF THE NAVY": "Department of the Navy",
    "DEPT OF HOMELAND SECURITY": "Department of Homeland Security",
    "DEPARTMENT OF HOMELAND SECURITY": "Department of Homeland Security",
    "DEPT OF VETERANS AFFAIRS": "Department of Veterans Affairs",
    "DEPARTMENT OF VETERANS AFFAIRS": "Department of Veterans Affairs",
    "DEPT OF ENERGY": "Department of Energy",
    "DEPARTMENT OF ENERGY": "Department of Energy",
    "DEPT OF STATE": "Department of State",
    "DEPARTMENT OF STATE": "Department of State",
    "DEPT OF JUSTICE": "Department of Justice",
    "DEPARTMENT OF JUSTICE": "Department of Justice",
    "DEPT OF TRANSPORTATION": "Department of Transportation",
    "GENERAL SERVICES ADMINISTRATION": "General Services Administration",
    "GSA": "General Services Administration",
    "NASA": "National Aeronautics and Space Administration",
    "NATIONAL AERONAUTICS AND SPACE ADMINISTRATION": "National Aeronautics and Space Administration",
}

# SAM.gov sbaBusinessTypeList codes for socioeconomic certifications
_CERT_TO_SAM_CODE: dict[str, str] = {
    "8(a)": "A5",
    "8A": "A5",
    "SDVOSB": "QF",
    "SERVICE-DISABLED VETERAN-OWNED": "QF",
    "WOSB": "A2",
    "WOMAN-OWNED": "A2",
    "HUBZONE": "XX",
    "HUBZone": "XX",
}


def _normalize_agency(agency_raw: str | None) -> str | None:
    """Extract top-level agency from SAM.gov fullParentPathName."""
    if not agency_raw:
        return None
    top = agency_raw.split(":")[0].strip().upper()
    return _AGENCY_MAP.get(top)


def _format_date(raw: str | None) -> str:
    """Convert ISO date string to 'Mon YYYY' display format."""
    if not raw:
        return ""
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).strftime("%b %Y")
    except Exception:
        return raw[:7]  # fallback: "YYYY-MM"


# ---------------------------------------------------------------------------
# Call A: USASpending — incumbents + teaming pairs
# ---------------------------------------------------------------------------

async def _fetch_primes(
    client: httpx.AsyncClient,
    naics_code: str,
    agency_usaspending: str | None,
) -> list[dict]:
    """Step 1: top prime award winners at same agency + NAICS."""
    filters: dict = {
        "naics_codes": [naics_code],
        "time_period": [{"start_date": "2021-01-01", "end_date": datetime.now().strftime("%Y-%m-%d")}],
        "award_type_codes": ["A", "B", "C", "D"],
    }
    if agency_usaspending:
        filters["agencies"] = [{"type": "awarding", "tier": "toptier", "name": agency_usaspending}]

    payload = {
        "filters": filters,
        "fields": ["Recipient Name", "Award Amount", "generated_internal_id", "Period of Performance Start Date"],
        "limit": 5,
        "sort": "Award Amount",
        "order": "desc",
    }

    resp = await client.post(
        "https://api.usaspending.gov/api/v2/search/spending_by_award/",
        json=payload,
        timeout=8.0,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])

    # If agency filter returned nothing, retry NAICS-only (still useful signal)
    if not results and agency_usaspending:
        payload["filters"].pop("agencies", None)
        resp = await client.post(
            "https://api.usaspending.gov/api/v2/search/spending_by_award/",
            json=payload,
            timeout=8.0,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])

    return results


async def _fetch_subawards(
    client: httpx.AsyncClient,
    award_id: str,
    prime_name: str,
) -> list[dict]:
    """Step 2: subawards for one prime award. NOTE: subawards API uses POST."""
    try:
        resp = await client.post(
            "https://api.usaspending.gov/api/v2/subawards/",
            json={"award_id": award_id, "limit": 3},
            timeout=4.0,
        )
        resp.raise_for_status()
        subs = resp.json().get("results", [])
        pairs = []
        seen: set[tuple[str, str]] = set()
        for s in subs:
            sub_name = (s.get("recipient_name") or "").title()
            contract = s.get("subaward_number") or award_id[:20]
            key = (prime_name.upper(), sub_name.upper())
            if sub_name and key not in seen and sub_name.upper() != prime_name.upper():
                seen.add(key)
                pairs.append({"prime": prime_name, "sub": sub_name, "contract": contract})
        return pairs
    except Exception as exc:
        logger.debug("Subaward fetch failed for %s: %s", award_id, exc)
        return []


async def _call_a_chain(
    client: httpx.AsyncClient,
    naics_code: str,
    agency_usaspending: str | None,
) -> tuple[list[dict], list[dict]]:
    """Full USASpending chain: primes then parallel subaward lookups."""
    prime_results = await _fetch_primes(client, naics_code, agency_usaspending)
    if not prime_results:
        return [], []

    # Incumbents from prime results
    incumbents = [
        {
            "name": (r.get("Recipient Name") or "").title(),
            "award_amount": float(r.get("Award Amount") or 0),
            "awarded": _format_date(r.get("Period of Performance Start Date")),
        }
        for r in prime_results
    ]

    # Subawards for top 3 prime awards in parallel
    top3 = prime_results[:3]
    sub_tasks = [
        _fetch_subawards(
            client,
            r["generated_internal_id"],
            (r.get("Recipient Name") or "").title(),
        )
        for r in top3
        if r.get("generated_internal_id")
    ]
    sub_results: list[list[dict]] = list(await asyncio.gather(*sub_tasks))

    # Deduplicate teaming pairs across prime awards
    teaming_pairs: list[dict] = []
    seen_pairs: set[tuple[str, str]] = set()
    for pairs in sub_results:
        for p in pairs:
            key = (p["prime"].upper(), p["sub"].upper())
            if key not in seen_pairs:
                seen_pairs.add(key)
                teaming_pairs.append(p)

    return incumbents, teaming_pairs


# ---------------------------------------------------------------------------
# Call B: SAM.gov — partner suggestions
# ---------------------------------------------------------------------------

async def _call_b_partners(
    client: httpx.AsyncClient,
    naics_code: str,
    user_naics: list[str],
    user_certs: list[str],
) -> list[dict]:
    """SAM.gov entity search for partner suggestions."""
    if not SAM_API_KEY:
        return []

    # If user already covers this NAICS, use 4-digit prefix for broader search.
    # SAM.gov supports prefix matching (naicsCode=5415 matches 541511, 541512, etc.)
    search_naics = naics_code[:4] if naics_code in user_naics else naics_code

    # Map user certifications to SAM.gov sbaBusinessTypeList codes
    cert_codes = list({
        code
        for cert in user_certs
        for key, code in _CERT_TO_SAM_CODE.items()
        if cert.upper() == key.upper()
    })

    params: dict[str, str] = {
        "api_key": SAM_API_KEY,
        "naicsCode": search_naics,
        "samRegistered": "Yes",
        "entityEFTIndicator": "~",  # SAM.gov: "~" = do not filter by EFT indicator
        "limit": "10",  # fetch more so we can filter incumbents out afterward
    }
    if cert_codes:
        params["sbaBusinessTypeList"] = ",".join(cert_codes)

    resp = await client.get(
        "https://api.sam.gov/entity-information/v3/entities",
        params=params,
        timeout=8.0,
    )
    resp.raise_for_status()
    entities = resp.json().get("entityData", [])

    suggestions = []
    for entity in entities:
        reg = entity.get("entityRegistration", {})
        name = reg.get("legalBusinessName") or ""
        if not name:
            continue

        # Extract primary NAICS
        naics_list = (
            entity.get("assertions", {})
            .get("goodsAndServices", {})
            .get("naicsList") or []
        )
        primary_naics = naics_list[0].get("naicsCode", search_naics) if naics_list else search_naics

        # Reflect the certs we searched for (if we filtered by cert, all results have it)
        cert_display = [
            k for k, v in _CERT_TO_SAM_CODE.items()
            if v in cert_codes and k in ("8(a)", "SDVOSB", "WOSB", "HUBZone")
        ]

        suggestions.append({"name": name, "naics": primary_naics, "certs": cert_display})
        if len(suggestions) >= 10:
            break

    return suggestions


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.get("/intel/{sam_id}", response_model=IntelResponse)
async def get_intel(
    sam_id: str,
    profile_id: int | None = None,
    db: Session = Depends(get_db),
):
    # 1. Load user profile (optional — partner suggestions fall back to
    # generic defense-industry matches when no profile_id is provided)
    if profile_id is not None:
        profile_row = db.execute(
            text("SELECT naics_codes, certifications FROM user_profiles WHERE id = :pid"),
            {"pid": profile_id},
        ).fetchone()
    else:
        profile_row = None
    user_naics: list[str] = list(profile_row.naics_codes or []) if profile_row else []
    user_certs: list[str] = list(profile_row.certifications or []) if profile_row else []

    # 2. Load opportunity metadata + cache columns
    opp_row = db.execute(
        text("""
            SELECT naics_code, agency, intel_data, intel_cached_at
            FROM opportunities
            WHERE sam_id = :sid
        """),
        {"sid": sam_id},
    ).fetchone()

    if not opp_row:
        return IntelResponse(error="intel_unavailable")

    # 3. Cache check (7-day TTL)
    if opp_row.intel_data and opp_row.intel_cached_at:
        cached_at = opp_row.intel_cached_at
        if cached_at.tzinfo is None:
            cached_at = cached_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - cached_at < timedelta(days=7):
            c = opp_row.intel_data
            return IntelResponse(
                incumbents=[IncumbentOut(**i) for i in c.get("incumbents", [])],
                teaming_pairs=[TeamingPairOut(**t) for t in c.get("teaming_pairs", [])],
                partner_suggestions=[PartnerSuggestionOut(**p) for p in c.get("partner_suggestions", [])],
                cached_at=c.get("cached_at"),
                partner_suggestions_unavailable=c.get("partner_suggestions_unavailable", False),
            )

    # 4. Live fetch — fire Call A and Call B in parallel
    naics_code = opp_row.naics_code or "541511"
    agency_usaspending = _normalize_agency(opp_row.agency)

    incumbents: list[dict] = []
    teaming_pairs: list[dict] = []
    partner_suggestions: list[dict] = []
    partner_suggestions_unavailable = False

    async with httpx.AsyncClient() as client:

        async def _a():
            return await asyncio.wait_for(
                _call_a_chain(client, naics_code, agency_usaspending),
                timeout=12.0,
            )

        async def _b():
            # Pass empty incumbent list — we filter post-gather
            return await _call_b_partners(client, naics_code, user_naics, user_certs)

        a_result, b_result = await asyncio.gather(_a(), _b(), return_exceptions=True)

    # --- Handle Call A result ---
    if isinstance(a_result, asyncio.TimeoutError):
        return IntelResponse(error="intel_unavailable")

    if isinstance(a_result, httpx.HTTPStatusError) and a_result.response.status_code == 429:
        # Retry once after 2s
        await asyncio.sleep(2)
        async with httpx.AsyncClient() as client:
            try:
                a_result = await asyncio.wait_for(
                    _call_a_chain(client, naics_code, agency_usaspending),
                    timeout=12.0,
                )
            except Exception:
                return IntelResponse(error="rate_limited")

    if isinstance(a_result, Exception):
        logger.warning("USASpending fetch failed for %s: %s", sam_id, a_result)
        return IntelResponse(error="intel_unavailable")

    incumbents, teaming_pairs = a_result

    # --- Handle Call B result ---
    incumbent_name_set = {inc["name"].upper() for inc in incumbents}

    if isinstance(b_result, Exception):
        logger.warning("SAM.gov partner fetch failed for %s: %s", sam_id, b_result)
        # Fallback: derive suggestions from subaward teaming pairs we already fetched.
        # Subs that worked on related contracts are high-quality partner candidates.
        seen_names: set[str] = set()
        for pair in teaming_pairs:
            for company in (pair.get("sub"), pair.get("prime")):
                if not company:
                    continue
                key = company.upper()
                if key not in seen_names and key not in incumbent_name_set:
                    seen_names.add(key)
                    partner_suggestions.append({"name": company, "naics": naics_code, "certs": []})
                if len(partner_suggestions) >= 5:
                    break
            if len(partner_suggestions) >= 5:
                break
        # Only mark unavailable if we truly have nothing to show
        if not partner_suggestions:
            partner_suggestions_unavailable = True
    else:
        partner_suggestions = [
            p for p in b_result
            if p["name"].upper() not in incumbent_name_set
        ][:5]

    # 5. Assemble and cache
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result_dict = {
        "incumbents": incumbents,
        "teaming_pairs": teaming_pairs,
        "partner_suggestions": partner_suggestions,
        "cached_at": now_str,
        "partner_suggestions_unavailable": partner_suggestions_unavailable,
    }

    # Cache write: swallow errors — user still gets their data
    try:
        db.execute(
            text("""
                UPDATE opportunities
                SET intel_data = CAST(:data AS JSONB),
                    intel_cached_at = NOW()
                WHERE sam_id = :sid
            """),
            {"data": json.dumps(result_dict), "sid": sam_id},
        )
        db.commit()
    except Exception as exc:
        logger.error("Intel cache write failed for %s: %s", sam_id, exc)

    return IntelResponse(
        incumbents=[IncumbentOut(**i) for i in incumbents],
        teaming_pairs=[TeamingPairOut(**t) for t in teaming_pairs],
        partner_suggestions=[PartnerSuggestionOut(**p) for p in partner_suggestions],
        cached_at=now_str,
        partner_suggestions_unavailable=partner_suggestions_unavailable,
    )
