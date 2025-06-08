from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db import engine
from app.models import Base
from app.routers.members import router as members_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Member Service",
    version="0.1.0",
    lifespan=lifespan,
)

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(members_router, prefix="/members", tags=["members"])
