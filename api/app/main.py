from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

motor_client: Optional[AsyncIOMotorClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global motor_client
    motor_client = AsyncIOMotorClient(settings.mongodb_url)
    await motor_client.admin.command("ping")
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

