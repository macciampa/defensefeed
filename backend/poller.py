import os
import logging
from datetime import datetime, timezone, timedelta

import httpx
from apscheduler.schedulers.background import BackgroundScheduler

from database import SessionLocal
from models import Opportunity
from embeddings import embed_texts_batch, build_opportunity_embedding_text

logger = logging.getLogger(__name__)

SAM_API_BASE = "https://api.sam.gov/opportunities/v2/search"
SAM_DATE_FORMAT = "%m/%d/%Y"
_scheduler: BackgroundScheduler | None = None


def _parse_deadline(value: str | None) -> datetime | None:
    """Parse responseDeadLine: ISO 8601 with offset e.g. '2026-04-15T16:00:00-04:00'."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        pass
    # Fallback: try date-only
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _parse_posted_date(value: str | None) -> datetime | None:
    """Parse postedDate: date string e.g. '2026-04-07'."""
    if not value:
        return None
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        pass
    # Fallback: try ISO
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


def poll_sam_gov() -> None:
    """Fetch SAM.gov opportunities, embed them, and upsert into the database."""
    api_key = os.getenv("SAM_API_KEY", "")
    if not api_key:
        logger.warning("SAM_API_KEY not set — skipping poll")
        return

    now = datetime.now(timezone.utc)
    posted_from = (now - timedelta(days=90)).strftime(SAM_DATE_FORMAT)
    posted_to = now.strftime(SAM_DATE_FORMAT)

    logger.info("Starting SAM.gov poll: postedFrom=%s postedTo=%s", posted_from, posted_to)

    all_opps: list[dict] = []
    offset = 0
    limit = 100
    total_records: int | None = None

    try:
        with httpx.Client(timeout=30) as http:
            while True:
                params = {
                    "api_key": api_key,
                    "postedFrom": posted_from,
                    "postedTo": posted_to,
                    "limit": limit,
                    "offset": offset,
                }
                # Retry with backoff on 429
                for attempt in range(4):
                    resp = http.get(SAM_API_BASE, params=params)
                    if resp.status_code == 429:
                        wait = 15 * (2 ** attempt)
                        logger.warning("SAM.gov 429 — waiting %ds (attempt %d/4)", wait, attempt + 1)
                        import time; time.sleep(wait)
                        continue
                    break
                resp.raise_for_status()
                data = resp.json()

                if total_records is None:
                    total_records = data.get("totalRecords", 0)
                    logger.info("SAM.gov total records available: %d", total_records)

                batch = data.get("opportunitiesData") or []
                if not batch:
                    break

                all_opps.extend(batch)
                logger.debug("Fetched %d so far (offset=%d)", len(all_opps), offset)

                offset += len(batch)
                if offset >= (total_records or 0):
                    break

    except Exception as exc:
        logger.warning("SAM.gov fetch skipped: %s", exc)
        return

    logger.info("Fetched %d total opportunities from SAM.gov", len(all_opps))

    if not all_opps:
        return

    db = SessionLocal()
    try:
        cutoff = now - timedelta(hours=24)

        # Determine which opportunities need upsert
        to_process: list[dict] = []
        for opp in all_opps:
            sam_id = opp.get("noticeId")
            if not sam_id:
                continue

            existing: Opportunity | None = (
                db.query(Opportunity).filter(Opportunity.sam_id == sam_id).first()
            )
            if existing and existing.synced_at and existing.synced_at >= cutoff:
                # Already synced within 24 hours — skip
                continue

            to_process.append(opp)

        logger.info("%d opportunities need upsert (out of %d fetched)", len(to_process), len(all_opps))

        if not to_process:
            return

        # Build embedding texts
        texts = [
            build_opportunity_embedding_text(
                title=opp.get("title", ""),
                description=opp.get("description"),
                naics_code=opp.get("naicsCode"),
                set_aside_type=opp.get("typeOfSetAside"),
            )
            for opp in to_process
        ]

        # Batch embed
        try:
            embeddings = embed_texts_batch(texts)
        except Exception as exc:
            logger.error("Embedding batch failed: %s", exc, exc_info=True)
            embeddings = [None] * len(to_process)  # type: ignore[list-item]

        # Upsert each opportunity
        upserted = 0
        for opp, embedding in zip(to_process, embeddings):
            sam_id = opp.get("noticeId")
            try:
                existing = (
                    db.query(Opportunity).filter(Opportunity.sam_id == sam_id).first()
                )
                if existing is None:
                    existing = Opportunity(sam_id=sam_id)
                    db.add(existing)

                existing.title = opp.get("title")
                existing.agency = opp.get("fullParentPathName")
                existing.naics_code = opp.get("naicsCode")
                existing.set_aside_type = opp.get("typeOfSetAside")
                existing.response_deadline = _parse_deadline(opp.get("responseDeadLine"))
                existing.posted_date = _parse_posted_date(opp.get("postedDate"))
                existing.description = opp.get("description")
                existing.sam_link = opp.get("uiLink")
                existing.opportunity_embedding = embedding
                existing.synced_at = now

                upserted += 1
            except Exception as exc:
                logger.warning("Failed to upsert opportunity %s: %s", sam_id, exc)
                db.rollback()
                continue

        db.commit()
        logger.info("Upserted %d opportunities into DB", upserted)

    except Exception as exc:
        logger.error("DB upsert error: %s", exc, exc_info=True)
        db.rollback()
    finally:
        db.close()


def start_scheduler() -> None:
    """Start the background scheduler and run the poller immediately on startup."""
    global _scheduler

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        poll_sam_gov,
        trigger="interval",
        hours=1,
        id="sam_gov_poll",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("APScheduler started — SAM.gov poll every hour")

    # Run immediately in a background thread so startup is not blocked
    import threading
    t = threading.Thread(target=poll_sam_gov, daemon=True, name="sam-poll-startup")
    t.start()
    logger.info("Initial SAM.gov poll started in background thread")


def stop_scheduler() -> None:
    """Shut down the background scheduler gracefully."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")
    _scheduler = None
