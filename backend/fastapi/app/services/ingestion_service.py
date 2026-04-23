import feedparser
import httpx
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional
import hashlib
import json
from aiokafka import AIOKafkaProducer
from app.repositories.article_repository import ArticleRepository
from app.repositories.cache_repository import CacheRepository
from app.models.article import Article, ArticleCreate
from app.core.config import settings

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self, repository: ArticleRepository, cache: CacheRepository, producer: Optional[AIOKafkaProducer] = None):
        self.repository = repository
        self.cache = cache
        self.producer = producer
        self.sources = [
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
            {"name": "Google News Tech", "url": "https://news.google.com/rss/search?q=technology&hl=en-US&gl=US&ceid=US:en"},
            {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"}
        ]

    async def ingest_all(self):
        logger.info("Starting global news ingestion with AI Refactoring & Caching...")
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
        logger.info(f"Source {source['name']} returned {len(feed.entries)} entries.")
        
        new_articles = 0
        # Limit to 25 per source for richer content
        for entry in feed.entries[:25]:
            article_id = entry.get("id", entry.link)
            
            # Check if exists
            existing = await self.repository.get_by_id(article_id)
            if existing:
                continue

            # Process
            article_data = await self._process_entry(client, entry, source["name"])
            if article_data:
                await self.repository.create(article_data)
                
                # TRIGGER PDF GENERATION
                if self.producer:
                    try:
                        # We send the dictionary representation of the article
                        # Article model has a convenient .dict() or .model_dump()
                        message = article_data.model_dump()
                        # Convert datetime to string for JSON serialization
                        message['publishedAt'] = message['publishedAt'].isoformat()
                        
                        await self.producer.send_and_wait(
                            "tex_rendering_queue",
                            json.dumps(message).encode("utf-8")
                        )
                        logger.info(f"PDF rendering task queued for: {article_data.title}")
                    except Exception as e:
                        logger.error(f"Failed to queue PDF task: {e}")

                new_articles += 1
                
        return new_articles

    async def _process_entry(self, client: httpx.AsyncClient, entry, source_name: str) -> Optional[Article]:
        title = entry.title
        summary_html = entry.get("summary", "") or entry.get("description", "")
        soup = BeautifulSoup(summary_html, "html.parser")
        description = soup.get_text()
        content = description # RSS usually only has summary
        
        # 1. AI Refactoring with Ollama + Cache
        refactored = await self._refactor_with_ai(client, title, description)
        final_title = refactored.get("title", title)
        final_desc = refactored.get("description", description)

        # 2. Robust Image Handling
        url_to_image = None
        
        # Method A: media_content / media_thumbnail
        if entry.get("media_content"):
            url_to_image = entry.media_content[0].get("url")
        elif entry.get("media_thumbnail"):
            url_to_image = entry.media_thumbnail[0].get("url")
        
        # Method B: Enclosures
        if not url_to_image and entry.get("enclosures"):
            for enc in entry.enclosures:
                if enc.get("type", "").startswith("image/"):
                    url_to_image = enc.get("url")
                    break

        # Method C: Parse from HTML summary/content
        if not url_to_image:
            img_tag = soup.find("img")
            if img_tag and img_tag.get("src"):
                url_to_image = img_tag["src"]

        # Method D: Fallback to high-quality curated stock images
        if not url_to_image:
            fallbacks = [
                "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=1000",
                "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=1000",
                "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=1000",
                "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=1000",
                "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&q=80&w=1000"
            ]
            # Use hash of title to pick a consistent fallback per article
            idx = hash(title) % len(fallbacks)
            url_to_image = fallbacks[idx]

        published_at = datetime.now()
        if entry.get("published_parsed"):
            published_at = datetime(*entry.published_parsed[:6])

        return Article(
            articleId=entry.get("id", entry.link),
            author=f"AI Journalist ({source_name})",
            title=final_title,
            description=final_desc,
            url=entry.link,
            urlToImage=url_to_image,
            publishedAt=published_at,
            content=content,
            source=source_name,
            category="technology"
        )

    async def _refactor_with_ai(self, client: httpx.AsyncClient, title: str, description: str) -> dict:
        # Create a unique key for the cache based on title and description
        cache_input = f"{title}|{description}"
        cache_key = hashlib.md5(cache_input.encode()).hexdigest()
        
        # Check cache
        cached_response = await self.cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache HIT for AI refactor: {title[:30]}...")
            return cached_response

        logger.info(f"Cache MISS for AI refactor: {title[:30]}...")
        
        prompt = f"""
        Eres un periodista de tecnología de alto nivel. Reescribe el siguiente título y descripción EN ESPAÑOL para que suenen más profesionales, concisos y elegantes, manteniendo un tono de innovación.
        IMPORTANTE: 
        1. Mantén estrictamente la veracidad de la noticia.
        2. NO añadas nombres de empresas o eventos que no estén en el original (como 'Symmetry').
        3. El resultado debe estar íntegramente en ESPAÑOL.
        4. Responde ÚNICAMENTE en formato JSON con los campos 'title' y 'description'.
        
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
                timeout=120.0
            )
            
            if response.status_code == 200:
                import json
                result = response.json()
                refactored = json.loads(result["response"])
                
                # Save to cache
                await self.cache.set(cache_key, refactored)
                return refactored
            else:
                logger.error(f"Ollama returned status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"DEBUG_AI_REFACTOR_FAIL ({type(e).__name__}): {e}")
            
        return {"title": title, "description": description}

