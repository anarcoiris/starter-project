import asyncio
import json
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from aiokafka import AIOKafkaProducer
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PDF-Trigger-Script")

async def trigger_all():
    logger.info("Connecting to MongoDB and Kafka...")
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers
    )
    await producer.start()
    
    try:
        articles = await db['articles'].find().to_list(length=1000)
        logger.info(f"Found {len(articles)} articles to process.")
        
        for art in articles:
            # Prepare message
            message = {
                "articleId": art.get("articleId"),
                "title": art.get("title"),
                "author": art.get("author", "Agente Symmetry"),
                "content": art.get("content", ""),
                "publishedAt": art.get("publishedAt").isoformat() if art.get("publishedAt") else None
            }
            
            await producer.send_and_wait(
                "tex_rendering_queue",
                json.dumps(message).encode("utf-8")
            )
            logger.info(f"Queued: {art.get('title')[:50]}...")
            
    finally:
        await producer.stop()
        client.close()
        logger.info("Done.")

if __name__ == "__main__":
    asyncio.run(trigger_all())
