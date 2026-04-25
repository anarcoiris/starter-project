"""
Symmetry Platform — RSS Ingestion Worker

Periodically fetches news from configured RSS sources, processes them
with AI (via Ollama), and stores them in MongoDB. Queues PDF rendering
tasks to Redpanda for the TeX worker.
"""

import asyncio
import logging

from aiokafka import AIOKafkaProducer
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core.utils import retry_async
from app.repositories.article_repository import ArticleRepository
from app.repositories.cache_repository import CacheRepository
from app.services.ingestion_service import IngestionService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("IngestWorker")

INGEST_INTERVAL_SECONDS = 300  # 5 minutes


async def connect_producer() -> AIOKafkaProducer:
    """Create and start a Kafka producer (used with retry_async)."""
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers
    )
    await producer.start()
    return producer


async def run_periodic_ingestion():
    logger.info("Starting Periodic Ingest Worker...")

    # ── Initialize DB ────────────────────────────────────────────────────
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]

    # ── Initialize Kafka Producer with retry ─────────────────────────────
    producer = await retry_async(
        connect_producer,
        description="Kafka producer connection",
        max_attempts=15,
        base_delay=2.0,
    )
    logger.info("Kafka producer connected.")

    # ── Initialize Service ───────────────────────────────────────────────
    repo = ArticleRepository(db)
    cache = CacheRepository(db)
    service = IngestionService(repo, cache, producer=producer)

    # ── Main Loop ────────────────────────────────────────────────────────
    try:
        while True:
            try:
                logger.info("Triggering scheduled news ingestion...")
                new_articles = await service.ingest_all()
                logger.info(f"Ingestion complete. Added {new_articles} new articles.")
            except Exception as e:
                logger.error(f"Error during scheduled ingestion: {e}", exc_info=True)

            logger.info(f"Waiting {INGEST_INTERVAL_SECONDS}s for next cycle...")
            await asyncio.sleep(INGEST_INTERVAL_SECONDS)
    finally:
        logger.info("Shutting down ingest worker...")
        await producer.stop()
        client.close()


if __name__ == "__main__":
    asyncio.run(run_periodic_ingestion())
