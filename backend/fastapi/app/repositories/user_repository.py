from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import UserProfile
from datetime import datetime, timezone
from typing import Optional

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def get_by_id(self, user_id: str) -> Optional[UserProfile]:
        doc = await self.collection.find_one({"userId": user_id})
        if doc:
            return UserProfile(**doc)
        return None

    async def update_wallet(self, user_id: str, wallet_address: str) -> bool:
        result = await self.collection.update_one(
            {"userId": user_id},
            {
                "$set": {
                    "walletAddress": wallet_address,
                    "lastActive": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None

    async def update_activity(self, user_id: str):
        await self.collection.update_one(
            {"userId": user_id},
            {"$set": {"lastActive": datetime.now(timezone.utc)}},
            upsert=True
        )

    async def register_vote(self, user_id: str, article_id: str, vote_type: str) -> Optional[str]:
        # Fetch current user
        user = await self.get_by_id(user_id)
        if not user:
            return None
            
        voted_articles = user.votedArticles or {}
        previous_vote = voted_articles.get(article_id)
        
        # If voting the same thing again, it means remove vote
        if previous_vote == vote_type:
            new_vote = None
            del voted_articles[article_id]
        else:
            new_vote = vote_type
            voted_articles[article_id] = vote_type
            
        await self.collection.update_one(
            {"userId": user_id},
            {
                "$set": {
                    "votedArticles": voted_articles,
                    "lastActive": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        return previous_vote
