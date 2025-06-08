from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx

from app.config import SERVICES

router = APIRouter()


@router.api_route(
    "/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_request(service: str, path: str, request: Request):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    cfg = SERVICES[service]
    target_url = f"{cfg['url']}{cfg['strip_prefix']}/{path}"

    async with httpx.AsyncClient() as client:
        body = await request.body()
        headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
        resp = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            params=request.query_params,
            timeout=30.0,
        )

    return JSONResponse(status_code=resp.status_code, content=resp.json())
