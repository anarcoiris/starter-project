import asyncio
import json
import logging
import os
from aiokafka import AIOKafkaConsumer
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MongoSinkWorker")

load_dotenv()

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
PROCESSED_TOPIC = os.getenv("KAFKA_TOPIC_PROCESSED", "processed_twitter_data")
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
DB_NAME = os.getenv("MONGODB_DB_NAME", "symmetry")

async def main():
    logger.info("Iniciando Mongo Sink Worker...")
    
    # 1. Configurar MongoDB
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    db = mongo_client[DB_NAME]
    collection = db["intelligence"]
    
    # 2. Configurar Kafka Consumer
    consumer = AIOKafkaConsumer(
        PROCESSED_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        group_id="mongo_sink_group",
        auto_offset_reset='earliest'
    )
    
    await consumer.start()
    logger.info(f"Consumiendo de {PROCESSED_TOPIC} y guardando en Mongo...")

    try:
        async for msg in consumer:
            data = json.loads(msg.value.decode("utf-8"))
            
            logger.info(f"Guardando inteligencia de tweet {data.get('id')}...")
            
            # Upsert por ID de tweet
            await collection.update_one(
                {"id": data["id"]},
                {"$set": data},
                upsert=True
            )

    except Exception as e:
        logger.error(f"Error en Mongo Sink Worker: {e}")
    finally:
        await consumer.stop()
        mongo_client.close()

if __name__ == "__main__":
    asyncio.run(main())
