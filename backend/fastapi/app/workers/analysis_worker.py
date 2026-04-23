import asyncio
import json
import logging
import os
import httpx
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AnalysisWorker")

load_dotenv()

KAFKA_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "redpanda:9092")
RAW_TOPIC = os.getenv("KAFKA_TOPIC_RAW", "raw_twitter_data")
PROCESSED_TOPIC = os.getenv("KAFKA_TOPIC_PROCESSED", "processed_twitter_data")
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://ollama:11434")

async def analyze_sentiment(text):
    """Llama a Ollama para analizar el sentimiento del texto."""
    prompt = f"""
    Analiza el sentimiento del siguiente texto y responde ÚNICAMENTE con un JSON:
    {{"sentiment": "positivo|negativo|neutral", "score": -1.0 a 1.0, "reason": "breve explicación"}}
    
    Texto: "{text}"
    """
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "qwen2.5:3b",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )
            if response.status_code == 200:
                result = response.json()
                return json.loads(result["response"])
    except Exception as e:
        logger.error(f"Error llamando a Ollama: {e}")
    
    return {"sentiment": "unknown", "score": 0.0, "reason": "error"}

async def main():
    logger.info("Iniciando Analysis Worker...")
    
    consumer = AIOKafkaConsumer(
        RAW_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        group_id="sentiment_analysis_group",
        auto_offset_reset='earliest'
    )
    
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_SERVER)
    
    await consumer.start()
    await producer.start()
    
    logger.info(f"Consumiendo de {RAW_TOPIC}...")

    try:
        async for msg in consumer:
            raw_data = json.loads(msg.value.decode("utf-8"))
            text = raw_data.get("text", "")
            
            logger.info(f"Procesando tweet {raw_data.get('id')}...")
            
            # 1. Análisis de IA
            analysis = await analyze_sentiment(text)
            
            # 2. Enriquecer datos
            processed_data = {
                **raw_data,
                "analysis": analysis,
                "processed_at": str(asyncio.get_event_loop().time())
            }
            
            # 3. Enviar a topic procesado
            await producer.send_and_wait(PROCESSED_TOPIC, json.dumps(processed_data).encode("utf-8"))
            logger.info(f"Tweet {raw_data.get('id')} procesado con éxito: {analysis['sentiment']}")

    except Exception as e:
        logger.error(f"Error en Analysis Worker: {e}")
    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(main())
