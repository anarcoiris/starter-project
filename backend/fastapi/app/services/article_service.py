import json
import logging
from typing import List, Optional

from aiokafka import AIOKafkaProducer

from app.repositories.article_repository import ArticleRepository
from app.models.article import Article, ArticleCreate, ArticleRead
from app.core.config import settings

logger = logging.getLogger(__name__)


class ArticleService:
    def __init__(
        self,
        repository: ArticleRepository,
        producer: Optional[AIOKafkaProducer] = None,
    ):
        self.repository = repository
        self._producer = producer

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
        # if self._producer: await self._producer.send(...)
        return True

    async def trigger_pdf_generation(self, article_id: str):
        """Publish a PDF rendering task to the tex_rendering_queue."""
        # 1. Get article from DB
        article = await self.repository.get_by_id(article_id)
        if not article:
            return None
        
        # 2. Publish task via the shared producer
        if not self._producer:
            logger.error("KafkaProducer not available — cannot trigger PDF generation")
            return None

        task_data = article.model_dump()
        # Ensure publishedAt is string for JSON serialization
        if task_data.get('publishedAt'):
            task_data['publishedAt'] = str(task_data['publishedAt'])
            
        await self._producer.send_and_wait(
            "tex_rendering_queue",
            json.dumps(task_data).encode('utf-8')
        )
        logger.info(f"PDF task queued for article {article_id}")
        return True
