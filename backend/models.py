from datetime import datetime
from sqlalchemy import Integer, Text, ARRAY, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    naics_codes: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    focus_areas: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    certifications: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    profile_embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)


class Opportunity(Base):
    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sam_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    agency: Mapped[str | None] = mapped_column(Text, nullable=True)
    notice_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    naics_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    set_aside_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    posted_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    opportunity_embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


def create_tables(engine):
    Base.metadata.create_all(engine)
    with engine.connect() as conn:
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS opp_embedding_hnsw_idx "
                "ON opportunities USING hnsw (opportunity_embedding vector_cosine_ops);"
            )
        )
        # People Intelligence Layer: cache columns for GET /intel/{sam_id}
        # ORM model intentionally not updated for these JSONB columns;
        # all reads/writes use raw SQL (consistent with embedding queries).
        conn.execute(text("""
            ALTER TABLE opportunities
            ADD COLUMN IF NOT EXISTS intel_data JSONB,
            ADD COLUMN IF NOT EXISTS intel_cached_at TIMESTAMPTZ
        """))
        conn.commit()
