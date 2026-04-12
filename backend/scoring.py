import math
from datetime import datetime, timezone


def compute_score(similarity: float, posted_date: datetime | None, response_deadline: datetime | None) -> float:
    """
    Score = 0.85 * similarity + 0.10 * recency + 0.05 * urgency

    Similarity is the dominant signal so that different capability
    profiles produce visibly different feed rankings (personalization).
    Recency and deadline urgency act as lightweight tiebreakers.

    recency = exp(-days_since_posted / 30)  [1.0 when fresh, ~0.05 at 90 days]
    urgency = max(0, 1 - days_until_deadline / 14)  [0.0 beyond 2 weeks, 1.0 today]
    """
    now = datetime.now(timezone.utc)

    # Recency weight
    if posted_date:
        # Ensure timezone-aware
        if posted_date.tzinfo is None:
            posted_date = posted_date.replace(tzinfo=timezone.utc)
        days_since_posted = max(0, (now - posted_date).days)
        recency = math.exp(-days_since_posted / 30)
    else:
        recency = 0.5  # Unknown posting date: neutral weight

    # Deadline urgency
    urgency = 0.0
    if response_deadline:
        if response_deadline.tzinfo is None:
            response_deadline = response_deadline.replace(tzinfo=timezone.utc)
        days_until = (response_deadline - now).days
        if days_until >= 0:  # Not expired
            urgency = max(0.0, 1.0 - days_until / 14)
        # Expired opportunities: urgency stays 0

    return 0.85 * similarity + 0.10 * recency + 0.05 * urgency


def get_urgency_level(response_deadline: datetime | None) -> str:
    """Return 'red', 'yellow', or 'none' based on days until deadline."""
    if not response_deadline:
        return "none"
    now = datetime.now(timezone.utc)
    if response_deadline.tzinfo is None:
        response_deadline = response_deadline.replace(tzinfo=timezone.utc)
    days = (response_deadline - now).days
    if days < 0:
        return "none"  # Expired
    if days < 7:
        return "red"
    if days < 14:
        return "yellow"
    return "none"


def format_days_left(response_deadline: datetime | None) -> str | None:
    """Human-readable 'X days left' string."""
    if not response_deadline:
        return None
    now = datetime.now(timezone.utc)
    if response_deadline.tzinfo is None:
        response_deadline = response_deadline.replace(tzinfo=timezone.utc)
    days = (response_deadline - now).days
    if days < 0:
        return "Expired"
    if days == 0:
        return "Due today"
    if days == 1:
        return "1 day left"
    return f"{days} days left"
