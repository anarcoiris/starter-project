from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.mongo_schema import initialize_mongo_schema
from app.api.v1.endpoints import articles, ollama, ingest

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    app.state.motor_client = AsyncIOMotorClient(settings.mongodb_url)
    app.state.db = app.state.motor_client[settings.mongodb_db_name]
    
    # Verify connection
    await app.state.motor_client.admin.command("ping")
    
    # Initialize schema/indexes
    await initialize_mongo_schema(app.state.db)
    
    yield
    
    # Shutdown: Close connection
    app.state.motor_client.close()

app = FastAPI(
    title="Symmetry Platform API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# Base Router
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(articles.router, prefix="/articles", tags=["Articles"])
api_router.include_router(ollama.router, prefix="/ollama", tags=["Ollama"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])

app.include_router(api_router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "symmetry-platform-api"}
