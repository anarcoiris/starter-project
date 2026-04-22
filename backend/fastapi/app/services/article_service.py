from typing import List
from app.repositories.article_repository import ArticleRepository
from app.models.article import Article, ArticleCreate

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

