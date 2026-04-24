from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field

class RewardTransaction(BaseModel):
    amount: float
    reason: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    referenceId: Optional[str] = None # e.g. articleId

class UserReward(BaseModel):
    userId: str
    totalBalance: float = 0.0
    transactions: List[RewardTransaction] = []
    lastUpdated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClaimRequest(BaseModel):
    userId: str
    articleId: str
    readTime: float = 0.0 # Time in seconds
