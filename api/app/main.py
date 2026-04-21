from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.mongo_schema import initialize_mongo_schema

motor_client: Optional[AsyncIOMotorClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global motor_client
    motor_client = AsyncIOMotorClient(settings.mongodb_url)
    await motor_client.admin.command("ping")
    db = motor_client[settings.mongodb_db_name]
    await initialize_mongo_schema(db)
    yield
    if motor_client is not None:
        motor_client.close()
        motor_client = None


app = FastAPI(
    title="Symmetry prototype API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "symmetry-prototype-api"}


@app.get("/articles")
async def list_articles(limit: int = 10):
    if motor_client is None:
        return {"items": []}
    db = motor_client[settings.mongodb_db_name]
    cursor = db["articles"].find({}, {"_id": 0}).sort("publishedAt", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    return {"items": items}

