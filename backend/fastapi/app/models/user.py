from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserProfile(BaseModel):
    userId: str
    email: Optional[str] = None
    walletAddress: Optional[str] = None
    reputationScore: float = 1.0
    createdAt: datetime = Field(default_factory=datetime.now)
    lastActive: datetime = Field(default_factory=datetime.now)

class WalletUpdate(BaseModel):
    walletAddress: str
