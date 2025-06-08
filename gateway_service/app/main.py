import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth import get_current_user
from app.routes.proxy import router as proxy_router

# Load environment variables from .env
load_dotenv()

# Define service URL mappings (Docker Compose service names)
SERVICE_URLS = {
    "members": os.getenv("MEMBER_SERVICE_URL", "http://member_service:8001"),
    "organizations": os.getenv("MEMBER_SERVICE_URL", "http://member_service:8001"),
    "feedback": os.getenv("FEEDBACK_SERVICE_URL", "http://feedback_service:8002"),
}

app = FastAPI(
    title="API Gateway",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Enable CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

app.include_router(
    proxy_router,
    prefix="",
    dependencies=[Depends(get_current_user)],
    tags=["proxy"]
)