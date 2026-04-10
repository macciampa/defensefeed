import os
import json
import pymupdf  # PyMuPDF
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EXTRACTION_PROMPT = """You are an expert in US government contracting. Extract structured information from this capability statement PDF text.

Return ONLY a valid JSON object with these exact fields:
- "naics_codes": list of NAICS codes as strings (just the 6-digit numbers, e.g. ["541512", "541330"])
- "psc_codes": list of PSC codes as strings
- "focus_areas": list of technical/service focus areas as short phrases, max 10 items
- "certifications": list of small business certifications only (e.g. ["8(a)", "SDVOSB", "HUBZone", "WOSB"])
- "keywords": list of key capability keywords, max 15 items
- "company_name": company name as a string, or null if not found

If you cannot find NAICS codes, return an empty list and extract relevant keywords instead.
Return ONLY valid JSON. No explanation, no markdown, no code blocks."""


def parse_pdf_text(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes using PyMuPDF."""
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        if not text.strip():
            raise ValueError("PDF contains no extractable text (possibly scanned or image-only)")
        return text
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")


def extract_profile_from_text(text: str) -> dict:
    """Use GPT-4o to extract structured profile from capability statement text."""
    # Truncate to ~8000 chars to stay within context window for extraction
    truncated = text[:8000]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You extract structured data from defense contractor capability statements. Always return valid JSON.",
            },
            {
                "role": "user",
                "content": f"{EXTRACTION_PROMPT}\n\nCapability Statement text:\n{truncated}",
            },
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    result = json.loads(content)

    # Normalize: ensure all expected fields exist with correct types
    return {
        "naics_codes": result.get("naics_codes") or [],
        "psc_codes": result.get("psc_codes") or [],
        "focus_areas": result.get("focus_areas") or [],
        "certifications": result.get("certifications") or [],
        "keywords": result.get("keywords") or [],
        "company_name": result.get("company_name"),
    }
