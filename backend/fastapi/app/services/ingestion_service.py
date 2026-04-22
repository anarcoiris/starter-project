import feedparser
import httpx
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional
from app.repositories.article_repository import ArticleRepository
from app.models.article import ArticleCreate
from app.core.config import settings

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self, repository: ArticleRepository):
        self.repository = repository
        self.sources = [
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
            {"name": "Google News Tech", "url": "https://news.google.com/rss/search?q=technology&hl=en-US&gl=US&ceid=US:en"}
        ]

    async def ingest_all(self):
        logger.info("Starting global news ingestion...")
        total_new = 0
        async with httpx.AsyncClient() as client:
            for source in self.sources:
                try:
                    new_count = await self._ingest_source(client, source)
                    total_new += new_count
                except Exception as e:
                    logger.error(f"Error ingesting {source['name']}: {e}")
        return total_new

    async def _ingest_source(self, client: httpx.AsyncClient, source: dict) -> int:
        response = await client.get(source["url"])
        feed = feedparser.parse(response.text)
        
        new_articles = 0
        # Limit to 5 per source for demo/performance
        for entry in feed.entries[:5]:
            article_id = entry.get("id", entry.link)
            
            # Check if exists
            existing = await self.repository.get_by_id(article_id)
            if existing:
                continue

            # Process
            article_data = await self._process_entry(client, entry, source["name"])
            if article_data:
                await self.repository.create(article_data)
                new_articles += 1
                
        return new_articles

    async def _process_entry(self, client: httpx.AsyncClient, entry, source_name: str) -> Optional[ArticleCreate]:
        title = entry.title
        description = BeautifulSoup(entry.get("summary", ""), "html.parser").get_text()
        content = description # RSS usually only has summary
        
        # 1. AI Refactoring with Ollama
        refactored = await self._refactor_with_ai(client, title, description)
        final_title = refactored.get("title", title)
        final_desc = refactored.get("description", description)

        # 2. Image Handling
        url_to_image = entry.get("media_content", [{}])[0].get("url") if entry.get("media_content") else None
        if not url_to_image:
            # Fallback to high-quality tech stock image
            keywords = "technology,cyberpunk,future,hardware"
            url_to_image = f"https://loremflickr.com/800/600/{keywords}?lock={hash(title) % 1000}"

        published_at = datetime.now()
        if entry.get("published_parsed"):
            published_at = datetime(*entry.published_parsed[:6])

        return ArticleCreate(
            articleId=entry.get("id", entry.link),
            author=f"AI Journalist ({source_name})",
            title=final_title,
            description=final_desc,
            url=entry.link,
            urlToImage=url_to_image,
            publishedAt=published_at,
            content=content,
            source=source_name,
            category="Technology"
        )

    async def _refactor_with_ai(self, client: httpx.AsyncClient, title: str, description: str) -> dict:
        prompt = f"""
        Eres un periodista de élite de Symmetry. Reescribe el siguiente título y descripción de noticia para que sea técnico, elegante y con un toque futurista. 
        Mantén la veracidad pero mejora el impacto. 
        Responde ÚNICAMENTE en formato JSON con los campos 'title' y 'description'.
        
        NOTICIA ORIGINAL:
        Título: {title}
        Descripción: {description}
        """
        
        try:
            response = await client.post(
                f"{settings.ollama_host}/api/generate",
                json={
                    "model": "qwen2.5:3b",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                import json
                result = response.json()
                return json.loads(result["response"])
        except Exception as e:
            logger.error(f"Ollama refactoring failed: {e}")
            
        return {"title": title, "description": description}
