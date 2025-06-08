from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db import engine
from app.models import Base
from app.routers.feedback import router as feedback_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables (retry logic already ran in db.py)
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: nothing special for now

app = FastAPI(
    title="Feedback Service",
    version="0.1.0",
    lifespan=lifespan,
)

# Health-check endpoint stays at /health
@app.get("/health")
async def health():
    return {"status": "ok"}

# Mount all feedback routes under a single /feedback prefix
app.include_router(feedback_router, prefix="/feedback", tags=["feedback"])