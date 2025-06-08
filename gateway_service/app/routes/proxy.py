import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx

router = APIRouter()

# Use same SERVICE_URLS mapping or import if preferred
env_members = os.getenv("MEMBER_SERVICE_URL", "http://member_service:8001")
env_feedback = os.getenv("FEEDBACK_SERVICE_URL", "http://feedback_service:8002")
SERVICE_URLS = {
    "members": env_members,
    "organizations": env_members,
    "feedback": env_feedback,
}

@router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICE_URLS:
        raise HTTPException(status_code=404, detail="Service not found")
    target_url = f"{SERVICE_URLS[service]}/{path}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Forward body, query params, and headers
            response = await client.request(
                method=request.method,
                url=target_url,
                content=await request.body(),
                params=request.query_params,
                headers={k: v for k, v in request.headers.items() if k.lower() != 'host'},
            )
        return JSONResponse(status_code=response.status_code, content=response.json())
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Bad gateway")