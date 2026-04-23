import asyncio
import logging
from app.services.ingestion_service import IngestionService
from app.repositories.article_repository import ArticleRepository
from app.repositories.cache_repository import CacheRepository
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IngestWorker")

async def run_periodic_ingestion():
    logger.info("Starting Periodic Ingest Worker...")
    
    from aiokafka import AIOKafkaProducer
    
    # Initialize DB connection
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    
    # Initialize Kafka Producer
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers
    )
    await producer.start()
    
    # Initialize Service
    repo = ArticleRepository(db)
    cache = CacheRepository(db)
    service = IngestionService(repo, cache, producer=producer)
    
    while True:
        try:
            logger.info("Triggering scheduled news ingestion...")
            new_articles = await service.ingest_all()
            logger.info(f"Ingestion complete. Added {new_articles} new articles.")
        except Exception as e:
            logger.error(f"Error during scheduled ingestion: {e}")
            
        # Wait for 5 minutes
        logger.info("Waiting 5 minutes for next cycle...")
        await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(run_periodic_ingestion())
