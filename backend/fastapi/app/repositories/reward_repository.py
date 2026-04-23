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
        
        # Atomically prevent duplicate claims for the same reference_id
        query = {"userId": user_id}
        if reference_id:
            # Only match if this referenceId is NOT in any existing transaction
            query["transactions.referenceId"] = {"$ne": reference_id}

        result = await self.collection.update_one(
            query,
            {
                "$inc": {"totalBalance": amount},
                "$push": {"transactions": transaction.model_dump()},
                "$set": {"lastUpdated": datetime.now()}
            },
            upsert=True
        )
        
        # If modified_count is 0 and it wasn't an upsert, it means the referenceId already exists
        if result.modified_count == 0 and result.upserted_id is None:
            # Verify if it was indeed a duplicate
            existing = await self.collection.find_one({"userId": user_id, "transactions.referenceId": reference_id})
            if existing:
                return None # Signal duplicate
                
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

