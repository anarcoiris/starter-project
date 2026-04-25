import asyncio
import json
import logging
import os
from aiokafka import AIOKafkaProducer
import tweepy
from dotenv import load_dotenv

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TwitterWorker")

load_dotenv()

# Configuración de Twitter
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
KEYWORDS = ["crypto", "blockchain", "AI", "news", "economy"]

# Configuración de Kafka
KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
TOPIC = os.getenv("KAFKA_TOPIC_RAW", "raw_twitter_data")

class SymmetryStream(tweepy.StreamingClient):
    def __init__(self, bearer_token, producer, topic):
        super().__init__(bearer_token)
        self.producer = producer
        self.topic = topic

    async def on_tweet(self, tweet):
        data = {
            "id": tweet.id,
            "text": tweet.text,
            "author_id": tweet.author_id,
            "created_at": str(tweet.created_at) if tweet.created_at else None,
            "source": "twitter_stream"
        }
        logger.info(f"Nuevo tweet capturado: {tweet.id}")
        await self.producer.send_and_wait(self.topic, json.dumps(data).encode("utf-8"))

async def main():
    logger.info("Iniciando Twitter Worker...")
    
    # 1. Iniciar Productor de Kafka con reintentos
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_SERVER)
    
    retry_count = 0
    while True:
        try:
            await producer.start()
            logger.info(f"Conectado a Redpanda en {KAFKA_SERVER}")
            break
        except Exception as e:
            retry_count += 1
            logger.warning(f"Intento {retry_count} fallido para conectar a Redpanda: {e}. Reintentando en 5s...")
            await asyncio.sleep(5)


    try:
        # 2. Configurar Stream de Twitter (V2)
        stream = SymmetryStream(BEARER_TOKEN, producer, TOPIC)
        
        # Limpiar reglas antiguas
        rules = stream.get_rules()
        if rules.data:
            stream.delete_rules([r.id for r in rules.data])
        
        # Añadir nuevas reglas
        stream.add_rules([tweepy.StreamRule(f"{' OR '.join(KEYWORDS)} lang:en")])
        
        logger.info(f"Escuchando keywords: {KEYWORDS}")
        # Iniciar stream (v2 usa hilos internos, pero manejamos la salida)
        stream.filter(tweet_fields=["created_at", "author_id"])
        
    except Exception as e:
        logger.error(f"Error en Twitter Worker: {e}")
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(main())
