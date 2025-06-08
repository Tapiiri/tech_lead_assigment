import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from .db import engine
from .models import Base
from .routers.feedback import router as feedback_router

load_dotenv()  # Load environment variables from .env file

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- Startup ----
    # ensure all tables are created (and DB connect retry has already run in db.py)
    Base.metadata.create_all(bind=engine)
    yield
    # ---- Shutdown ----
    # any teardown logic can go here (not needed for now)

app = FastAPI(
    title="Feedback Service",
    version="0.1.0",
    lifespan=lifespan,
    openapi_prefix="/feedback"  # if you prefer your docs under /feedback
)

app.include_router(feedback_router)

@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}