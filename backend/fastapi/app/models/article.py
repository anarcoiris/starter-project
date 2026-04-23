from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ArticleBase(BaseModel):
    author: str
    title: str
    description: str
    urlToImage: str
    content: str
    publishedAt: datetime = Field(default_factory=datetime.now)
    category: str = "general"

class ArticleCreate(ArticleBase):
    """Schema for creating a new article via API. 
    Only user-contributed fields are present here.
    """
    source: str = "Symmetry User"
    sourceId: Optional[str] = None
    url: Optional[str] = None # Optional, system can generate one if missing

class Article(ArticleBase):
    """Full article model including system-managed fields."""
    articleId: str
    url: str
    source: str
    sourceId: Optional[str] = None
    views: int = 0
    readTime: int = 0
    tokensEarned: float = 0.0
    expectedReadTime: Optional[int] = 30
    qualityScore: Optional[float] = 1.0
    fraudScore: float = 0.0
    rewardEpoch: Optional[int] = 0
    verifiedImpressionCount: int = 0


    class Config:
        from_attributes = True

class ArticleRead(BaseModel):
    userId: str
    readTimeSeconds: int
    readAt: datetime = Field(default_factory=datetime.now)


