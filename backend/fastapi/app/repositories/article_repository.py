import logging
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.article import Article, ArticleCreate

logger = logging.getLogger(__name__)

class ArticleRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["articles"]

    async def get_all(self, category: str = None, limit: int = 10) -> List[Article]:
        query = {}
        if category:
            query["category"] = category
            
        cursor = self.collection.find(query, {"_id": 0}).sort("publishedAt", -1).limit(limit)
        items = await cursor.to_list(length=limit)
        return [Article(**item) for item in items]


    async def create(self, article: Article) -> Article:
        # Debugging: check what type we actually received
        logger.debug(f"Repository creating article of type: {type(article)}")
        
        try:
            # Handle both Pydantic models and dictionaries
            if hasattr(article, "model_dump"):
                doc = article.model_dump()
                article_id = getattr(article, "articleId", doc.get("articleId"))
            else:
                doc = dict(article)
                article_id = doc.get("articleId")

            if not article_id:
                # Fallback: maybe it's in the doc but was called incorrectly
                article_id = doc.get("articleId")
            
            if not article_id:
                raise AttributeError(f"Object of type {type(article)} has no articleId field")

            logger.debug(f"Saving document to Mongo: {doc}")
            
            # Ensure publishedAt is a datetime and not a string
            if isinstance(doc.get("publishedAt"), str):
                from datetime import datetime
                doc["publishedAt"] = datetime.fromisoformat(doc["publishedAt"].replace("Z", "+00:00"))
            
            await self.collection.update_one(
                {"articleId": article_id},
                {"$set": doc},
                upsert=True
            )
            return Article(**doc)
        except Exception as e:
            logger.error(f"MongoDB Error in repository: {e} (Type: {type(article)})")
            raise

    async def get_by_id(self, article_id: str) -> Optional[Article]:
        doc = await self.collection.find_one({"articleId": article_id}, {"_id": 0})
        return Article(**doc) if doc else None

    async def increment_read_metrics(self, article_id: str, read_time: int):
        """Atomically increment views and total read time."""
        await self.collection.update_one(
            {"articleId": article_id},
            {
                "$inc": {
                    "views": 1,
                    "readTime": read_time,
                    "verifiedImpressionCount": 1
                }
            }
        )


