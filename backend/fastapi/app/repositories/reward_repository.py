from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.reward import UserReward, RewardTransaction
from datetime import datetime
from typing import Optional

class RewardRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["rewards"]

    async def get_user_reward(self, user_id: str) -> UserReward:
        doc = await self.collection.find_one({"userId": user_id})
        if doc:
            return UserReward(**doc)
        return UserReward(userId=user_id)

    async def add_reward(self, user_id: str, amount: float, reason: str, reference_id: str = None):
        transaction = RewardTransaction(
            amount=amount,
            reason=reason,
            referenceId=reference_id,
            timestamp=datetime.now()
        )
        
        await self.collection.update_one(
            {"userId": user_id},
            {
                "$inc": {"totalBalance": amount},
                "$push": {"transactions": transaction.model_dump()},
                "$set": {"lastUpdated": datetime.now()}
            },
            upsert=True
        )
        return transaction

    async def transfer_reward(self, from_user_id: str, to_user_id: str, amount: float, reason: str):
        # 1. Deduct from sender
        negative_tx = RewardTransaction(
            amount=-amount,
            reason=f"Transfer to {to_user_id}: {reason}",
            timestamp=datetime.now()
        )
        await self.collection.update_one(
            {"userId": from_user_id},
            {
                "$inc": {"totalBalance": -amount},
                "$push": {"transactions": negative_tx.model_dump()},
                "$set": {"lastUpdated": datetime.now()}
            },
            upsert=True
        )

        # 2. Add to receiver
        positive_tx = RewardTransaction(
            amount=amount,
            reason=f"Transfer from {from_user_id}: {reason}",
            timestamp=datetime.now()
        )
        await self.collection.update_one(
            {"userId": to_user_id},
            {
                "$inc": {"totalBalance": amount},
                "$push": {"transactions": positive_tx.model_dump()},
                "$set": {"lastUpdated": datetime.now()}
            },
            upsert=True
        )
        return positive_tx

    async def has_received_airdrop(self, user_id: str) -> bool:
        doc = await self.collection.find_one({
            "userId": user_id,
            "transactions.reason": {"$regex": "Airdrop"}
        })
        return doc is not None

    async def get_airdrop_count(self) -> int:
        return await self.collection.count_documents({
            "transactions.reason": {"$regex": "Airdrop"}
        })

