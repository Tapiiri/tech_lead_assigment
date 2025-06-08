from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db import SessionLocal, engine
from app.models import Base
from app.routers.feedback import router as feedback_router
from app.seed import seed_feedback

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables (retry logic already ran in db.py)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_feedback(db)
    finally:
        db.close()
    yield

app = FastAPI(
    title="Feedback Service",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(feedback_router, prefix="/feedback", tags=["feedback"])