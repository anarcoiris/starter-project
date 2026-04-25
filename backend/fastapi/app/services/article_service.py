import json
import logging
from typing import List, Optional
import hashlib
from datetime import datetime

from aiokafka import AIOKafkaProducer

from app.repositories.article_repository import ArticleRepository
from app.repositories.user_repository import UserRepository
from app.models.article import Article, ArticleCreate, ArticleRead
from app.core.config import settings

logger = logging.getLogger(__name__)


class ArticleService:
    def __init__(
        self,
        repository: ArticleRepository,
        user_repo: UserRepository = None,
        producer: Optional[AIOKafkaProducer] = None,
    ):
        self.repository = repository
        self.user_repo = user_repo
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

    async def vote_article(self, article_id: str, user_id: str, vote_type: str) -> dict:
        if not self.user_repo:
            raise Exception("UserRepository not initialized in ArticleService")
            
        previous_vote = await self.user_repo.register_vote(user_id, article_id, vote_type)
        
        up_change = 0
        down_change = 0
        
        if previous_vote == vote_type:
            # User unvoted
            if vote_type == 'up': up_change = -1
            elif vote_type == 'down': down_change = -1
        else:
            # User changed vote or new vote
            if vote_type == 'up':
                up_change = 1
                if previous_vote == 'down': down_change = -1
            elif vote_type == 'down':
                down_change = 1
                if previous_vote == 'up': up_change = -1
                
        await self.repository.update_votes(article_id, up_change, down_change)
        return {"status": "success", "upChange": up_change, "downChange": down_change}
        
    async def generate_daily_newspaper(self):
        # Fetch top 10 articles of the last 24 hours (simplified to latest 10 for now)
        articles = await self.repository.get_all(limit=10)
        if not articles:
            return None
            
        # Create a special "newspaper" article to hold the PDF
        date_str = datetime.now().strftime("%Y-%m-%d")
        daily_id = f"anarcotimes-daily-{date_str}"
        
        # Check if already generated today
        existing = await self.repository.get_by_id(daily_id)
        if existing and existing.pdfPath:
            return existing
            
        newspaper_article = ArticleCreate(
            title=f"Anarcotimes - Edición Diaria {date_str}",
            description="La compilación de las noticias tecnológicas más importantes del día.",
            url=f"https://symmetry.news/daily/{date_str}",
            author="Redacción Symmetry",
            content="Ver PDF para el contenido completo.",
            urlToImage="https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&q=80&w=1000"
        )
        
        full_article = await self.create_article(newspaper_article)
        
        # Override fields for the special article
        await self.repository.collection.update_one(
            {"articleId": full_article.articleId},
            {"$set": {"articleId": daily_id, "category": "newspaper"}}
        )
        full_article.articleId = daily_id
        
        if not self._producer:
            logger.error("KafkaProducer not available")
            return full_article

        # Instead of just sending one article to tex worker, we ideally want a special task,
        # but for now, we'll queue the special article and the TeX worker would normally process it.
        # Since TeX worker currently processes single articles, we'll need to adapt it later or just 
        # queue it as is. We'll queue it as is.
        
        task_data = full_article.model_dump()
        task_data['publishedAt'] = str(task_data['publishedAt'])
            
        await self._producer.send_and_wait(
            "tex_rendering_queue",
            json.dumps(task_data).encode('utf-8')
        )
        return full_article
