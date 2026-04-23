from typing import List
from app.repositories.article_repository import ArticleRepository
from app.models.article import Article, ArticleCreate, ArticleRead
from app.core.config import settings
import json
from aiokafka import AIOKafkaProducer

class ArticleService:
    def __init__(self, repository: ArticleRepository):
        self.repository = repository

    async def list_latest_articles(self, category: str = None, limit: int = 10) -> List[Article]:
        return await self.repository.get_all(category=category, limit=limit)


    async def create_article(self, article_create: ArticleCreate) -> Article:
        import uuid
        
        # 1. Generate system fields
        article_id = str(uuid.uuid4())
        url = article_create.url or f"https://symmetry.news/article/{article_id}"
        
        # 2. Calculate expected read time (200 words per minute)
        words = len(article_create.content.split())
        estimated_seconds = max(10, (words // 200) * 60)
        
        # 3. Construct the full Article model
        article_dict = article_create.model_dump()
        article_dict.update({
            "articleId": article_id,
            "url": url,
            "expectedReadTime": estimated_seconds,
            "views": 0,
            "tokensEarned": 0.0,
            "qualityScore": 1.0,
            "fraudScore": 0.0
        })
        
        full_article = Article(**article_dict)
        return await self.repository.create(full_article)

    async def register_read_impact(self, article_id: str, event: ArticleRead):
        # 1. Update counters in DB
        await self.repository.increment_read_metrics(article_id, event.readTimeSeconds)
        
        # 2. TODO: Publish to Redpanda for real-time fraud analysis
        # producer.send('read_events', event.json())
        return True

    async def trigger_pdf_generation(self, article_id: str):
        # 1. Get article from DB
        article = await self.repository.get_by_id(article_id)
        if not article:
            return None
        
        # 2. Publish task to Redpanda
        producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
        await producer.start()
        try:
            task_data = article.model_dump()
            # Ensure publishedAt is string for JSON
            if task_data.get('publishedAt'):
                task_data['publishedAt'] = str(task_data['publishedAt'])
                
            await producer.send_and_wait("tex_rendering_queue", json.dumps(task_data).encode('utf-8'))
        finally:
            await producer.stop()
            
        return True


