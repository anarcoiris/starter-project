from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import UserProfile
from datetime import datetime
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
                    "lastActive": datetime.now()
                }
            },
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None

    async def update_activity(self, user_id: str):
        await self.collection.update_one(
            {"userId": user_id},
            {"$set": {"lastActive": datetime.now()}},
            upsert=True
        )
