from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.models.article import Article, ArticleCreate, ArticleRead
from app.services.article_service import ArticleService
from app.api.deps import get_article_service

router = APIRouter()

@router.get("/", response_model=List[Article])
async def list_articles(
    category: str = None,
    limit: int = 10, 
    service: ArticleService = Depends(get_article_service)
):
    return await service.list_latest_articles(category=category, limit=limit)


@router.post("/", response_model=Article)
async def create_article(article: ArticleCreate, service: ArticleService = Depends(get_article_service)):
    return await service.create_article(article)

@router.post("/{article_id}/read")
async def register_read_event(
    article_id: str, 
    event: ArticleRead, 
    service: ArticleService = Depends(get_article_service)
):
    """
    Registers a read event for an article to track impact and rewards.
    """
    await service.register_read_impact(article_id, event)
    return {"status": "success", "message": "Impact registered"}

@router.post("/{article_id}/pdf")
async def trigger_article_pdf(
    article_id: str,
    service: ArticleService = Depends(get_article_service)
):
    """
    Triggers the generation of a newspaper-style PDF for the article.
    """
    success = await service.trigger_pdf_generation(article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return {"status": "success", "message": "PDF rendering task queued in Anarcotimes"}

class VoteRequest(BaseModel):
    userId: str
    vote: str # 'up' or 'down'

@router.post("/{article_id}/vote")
async def vote_on_article(
    article_id: str,
    request: VoteRequest,
    service: ArticleService = Depends(get_article_service)
):
    if request.vote not in ['up', 'down']:
        raise HTTPException(status_code=400, detail="Vote must be 'up' or 'down'")
        
    result = await service.vote_article(article_id, request.userId, request.vote)
    return result

@router.post("/generate-daily")
async def generate_daily_newspaper(
    service: ArticleService = Depends(get_article_service)
):
    """
    Generates a daily newspaper PDF compiling top articles.
    """
    article = await service.generate_daily_newspaper()
    if not article:
        raise HTTPException(status_code=400, detail="Could not generate daily newspaper")
        
    return {"status": "success", "articleId": article.articleId}
