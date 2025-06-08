import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.auth import get_current_user
from app.routes.proxy import router as proxy_router

# Map service names to URLs via environment or defaults
SERVICE_URLS = {
    "members": os.getenv("MEMBER_SERVICE_URL", "http://member_service:8001"),
    "feedback": os.getenv("FEEDBACK_SERVICE_URL", "http://feedback_service:8002"),
}

app = FastAPI(
    title="API Gateway",
    docs_url="/docs",
    openapi_url="/openapi.json"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

# All proxy routes are protected by JWT auth at the gateway
app.include_router(
    proxy_router,
    prefix="",
    dependencies=[Depends(get_current_user)],
    tags=["proxy"]
)