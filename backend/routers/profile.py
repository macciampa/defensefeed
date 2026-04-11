from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import get_db
from models import UserProfile
from schemas import ProfileResponse, ProfileExtraction
from extraction import parse_pdf_text, extract_profile_from_text
from embeddings import embed_text, build_profile_embedding_text

router = APIRouter()


@router.post("/profile", response_model=ProfileResponse)
async def upload_profile(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Validate file type
    if not (file.filename or "").endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files are accepted")

    # Read file bytes
    pdf_bytes = await file.read()
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=422, detail="Empty file uploaded")

    # Parse PDF text
    try:
        raw_text = parse_pdf_text(pdf_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Extract profile with GPT-4o
    try:
        extraction = extract_profile_from_text(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile extraction failed: {str(e)}")

    # Build embedding text and generate embedding
    profile_text = build_profile_embedding_text(
        naics_codes=extraction["naics_codes"],
        focus_areas=extraction["focus_areas"],
        certifications=extraction["certifications"],
        keywords=extraction["keywords"],
    )

    if not profile_text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not extract meaningful content from this PDF. Please ensure it's a capability statement.",
        )

    try:
        embedding = embed_text(profile_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

    # Insert a new profile row — each upload creates an independent tenant.
    # The caller stores the returned profile_id client-side and passes it on
    # subsequent /feed and /intel requests.
    profile = UserProfile(
        uploaded_at=datetime.now(timezone.utc),
        raw_text=raw_text,
        naics_codes=extraction["naics_codes"],
        focus_areas=extraction["focus_areas"],
        certifications=extraction["certifications"],
        profile_embedding=embedding,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    return ProfileResponse(
        profile_id=profile.id,
        extraction=ProfileExtraction(**extraction),
        uploaded_at=profile.uploaded_at.isoformat(),
    )


@router.get("/profile/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="No profile uploaded yet.")

    extraction = ProfileExtraction(
        naics_codes=profile.naics_codes or [],
        focus_areas=profile.focus_areas or [],
        certifications=profile.certifications or [],
    )

    return ProfileResponse(
        profile_id=profile.id,
        extraction=extraction,
        uploaded_at=profile.uploaded_at.isoformat() if profile.uploaded_at else "",
    )
