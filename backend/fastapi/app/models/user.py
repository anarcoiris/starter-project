from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone

class UserProfile(BaseModel):
    userId: str
    displayName: Optional[str] = None
    email: Optional[str] = None
    avatarUrl: Optional[str] = None
    bio: Optional[str] = None
    walletAddress: Optional[str] = None
    reputationScore: float = 1.0
    votedArticles: dict = {} # Map de articleId a 'up' o 'down'
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    lastActive: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WalletUpdate(BaseModel):
    walletAddress: str
