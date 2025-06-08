from collections import defaultdict
import os
import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import httpx

from app.routes.proxy import router as proxy_router
from app.config import SERVICES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_openapi_spec(service_url: str, retries=3, delay=2) -> dict:
    """Fetch OpenAPI spec with retries"""
    async with httpx.AsyncClient() as client:
        for attempt in range(retries):
            try:
                response = await client.get(f"{service_url}/openapi.json", timeout=10.0)
                if response.status_code == 200:
                    return response.json()
            except (httpx.RequestError, httpx.TimeoutException) as e:
                logger.warning(f"Attempt {attempt+1} failed for {service_url}: {e}")
                await asyncio.sleep(delay)
    raise RuntimeError(f"Failed to fetch OpenAPI spec from {service_url}")

def transform_schema_references(spec: dict, service_name: str) -> dict:
    """Recursively update schema references with service prefix"""
    if isinstance(spec, dict):
        for key, value in list(spec.items()):
            if key == "$ref" and isinstance(value, str):
                # Update schema references
                if "#/components/schemas/" in value:
                    schema_name = value.split("/")[-1]
                    spec[key] = f"#/components/schemas/{service_name}_{schema_name}"
            else:
                transform_schema_references(value, service_name)
    elif isinstance(spec, list):
        for item in spec:
            transform_schema_references(item, service_name)
    return spec

def transform_paths(spec: dict, prefix: str, strip_prefix: str) -> dict:
    """Transform paths to include gateway prefix and remove service prefix"""
    transformed = {}
    for path, methods in spec.get("paths", {}).items():
        # Remove service-specific prefix
        if strip_prefix and path.startswith(strip_prefix):
            path = path[len(strip_prefix):]
        # Add gateway prefix
        new_path = f"{prefix}{path}"
        transformed[new_path] = methods
        
        # Update server references
        for method in methods.values():
            if "servers" in method:
                del method["servers"]
    return transformed

async def generate_aggregated_openapi(app) -> dict:
    """Generate aggregated OpenAPI schema with proper schema references"""
    base_spec = get_openapi(
        title="API Gateway",
        version="1.0.0",
        routes=app.routes,
    )
    
    aggregated_paths = {}
    aggregated_components = defaultdict(dict)

    for service_name, config in SERVICES.items():
        try:
            # Fetch and transform service spec
            service_spec = await fetch_openapi_spec(config["url"])
            
            # Update all schema references in the entire spec
            service_spec = transform_schema_references(service_spec, service_name)
            
            # Transform paths
            transformed_paths = transform_paths(
                service_spec,
                config["prefix"],
                config["strip_prefix"]
            )
            
            # Merge paths
            aggregated_paths.update(transformed_paths)
            
            # Process components
            if "components" in service_spec:
                for component_type, components in service_spec["components"].items():
                    if component_type == "schemas":
                        # Prefix all schema names
                        for schema_name, schema_def in components.items():
                            new_name = f"{service_name}_{schema_name}"
                            aggregated_components["schemas"][new_name] = schema_def
                    else:
                        # Merge other components as-is
                        if component_type not in aggregated_components:
                            aggregated_components[component_type] = {}
                        aggregated_components[component_type].update(components)
                        
        except Exception as e:
            logger.error(f"Error processing {service_name} service: {e}")

    # Merge all components
    base_spec["paths"] = aggregated_paths
    base_spec["components"] = dict(aggregated_components)
    
    # Clean up potential null values
    if "servers" in base_spec and not base_spec["servers"]:
        del base_spec["servers"]
        
    return base_spec

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup logic ---
    logger.info("Generating aggregated OpenAPI schema…")
    app.openapi_schema = await generate_aggregated_openapi(app)
    yield
    # --- (no shutdown actions needed) ---

app = FastAPI(
    title="API Gateway",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Allow any origin for convenience (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint to force-refresh the docs at runtime
@app.post("/refresh-docs")
async def refresh_docs():
    app.openapi_schema = await generate_aggregated_openapi(app)
    return {"status": "docs_refreshed"}

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

# All proxy routes are protected by JWT auth at the gateway
app.include_router(
    proxy_router,
    prefix="",
    tags=["proxy"]
)