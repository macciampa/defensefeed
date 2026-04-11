from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from models import create_tables
from routers import profile, feed, intel
import poller


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables(engine)
    poller.start_scheduler()
    yield
    # Shutdown
    poller.stop_scheduler()


app = FastAPI(title="Pryzm API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router)
app.include_router(feed.router)
app.include_router(intel.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/poll")
def trigger_poll():
    """Manually trigger a SAM.gov poll. Runs in background thread."""
    import threading
    t = threading.Thread(target=poller.poll_sam_gov, daemon=True)
    t.start()
    return {"status": "poll started"}


@app.get("/poll/status")
def poll_status():
    """Return opportunity count and last sync time."""
    from database import SessionLocal
    from models import Opportunity
    from sqlalchemy import func
    db = SessionLocal()
    try:
        total = db.query(func.count(Opportunity.id)).scalar()
        latest = db.query(func.max(Opportunity.synced_at)).scalar()
        return {"total_opportunities": total, "last_synced": latest}
    finally:
        db.close()
