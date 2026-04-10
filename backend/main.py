from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from models import create_tables
from routers import profile, feed
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


@app.get("/health")
def health_check():
    return {"status": "ok"}
