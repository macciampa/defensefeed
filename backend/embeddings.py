import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMS = 1536


def embed_text(text: str) -> list[float]:
    """Embed a single text string. Returns 1536-dim vector."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
        dimensions=EMBEDDING_DIMS,
    )
    return response.data[0].embedding


def embed_texts_batch(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. OpenAI handles up to 2048 inputs per call.
    We batch in groups of 100 to stay well within token limits (~500 tokens/opp)."""
    results = []
    for i in range(0, len(texts), 100):
        batch = texts[i:i + 100]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
            dimensions=EMBEDDING_DIMS,
        )
        # Sort by index to ensure order matches input
        sorted_data = sorted(response.data, key=lambda x: x.index)
        results.extend([item.embedding for item in sorted_data])
    return results


def build_profile_embedding_text(naics_codes: list[str], focus_areas: list[str],
                                  certifications: list[str], keywords: list[str]) -> str:
    """Build the canonical text to embed for a user profile.
    Format: 'NAICS: {codes}\\nFocus areas: {areas}\\nCertifications: {certs}\\nKeywords: {kws}'
    """
    parts = []
    if naics_codes:
        parts.append(f"NAICS: {', '.join(naics_codes)}")
    if focus_areas:
        parts.append(f"Focus areas: {', '.join(focus_areas)}")
    if certifications:
        parts.append(f"Certifications: {', '.join(certifications)}")
    if keywords:
        parts.append(f"Keywords: {', '.join(keywords)}")
    return "\n".join(parts) if parts else ""


def build_opportunity_embedding_text(title: str, description: str | None,
                                      naics_code: str | None, set_aside_type: str | None) -> str:
    """Build the text to embed for an opportunity."""
    parts = [title or ""]
    if description:
        # Truncate description to ~1500 chars to stay within token budget
        parts.append(description[:1500])
    if naics_code:
        parts.append(f"NAICS: {naics_code}")
    if set_aside_type:
        parts.append(f"Set-aside: {set_aside_type}")
    return " ".join(p for p in parts if p)
