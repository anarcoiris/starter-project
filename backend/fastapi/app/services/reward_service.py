import logging
from app.repositories.reward_repository import RewardRepository
from app.repositories.article_repository import ArticleRepository
from app.core.config import settings
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class RewardService:
    def __init__(self, reward_repo: RewardRepository, article_repo: ArticleRepository):
        self.reward_repo = reward_repo
        self.article_repo = article_repo

    async def claim_reading_reward(self, user_id: str, article_id: str, read_time: float = 0.0):
        # 1. Check if article exists
        article = await self.article_repo.get_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        # 2. Basic Scoring Layer: Minimum read time from settings
        if read_time < settings.min_read_time:
            logger.warning(f"Reward rejected for {user_id}: insufficient read time ({read_time}s)")
            raise HTTPException(
                status_code=400, 
                detail=f"Lectura demasiado breve para recompensa. Mínimo: {settings.min_read_time}s"
            )

        # 3. Apply reward (Atomic check inside repo)
        transaction = await self.reward_repo.add_reward(
            user_id=user_id,
            amount=settings.base_reward,
            reason="Article Read",
            reference_id=article_id
        )
        
        if transaction is None:
            raise HTTPException(status_code=400, detail="Reward already claimed for this article")
            
        return transaction



    async def get_balance(self, user_id: str):
        # 1. Trigger Airdrop Check (First 1,000 users)
        await self.process_airdrop(user_id)
        
        # 2. Get Balance
        user_reward = await self.reward_repo.get_user_reward(user_id)
        return {
            "userId": user_id,
            "balance": user_reward.totalBalance,
            "transactionCount": len(user_reward.transactions)
        }


    async def initialize_custodian(self, amount: float = 1000000.0):
        custodian_id = settings.custodian_email
        
        # Check if already initialized to avoid duplicates
        balance_data = await self.get_balance(custodian_id)
        if balance_data["balance"] > 0:
            return {"status": "already_initialized", "balance": balance_data["balance"]}
            
        await self.reward_repo.add_reward(
            user_id=custodian_id,
            amount=amount,
            reason="Initial Pre-mine"
        )
        return {"status": "initialized", "balance": amount}

    async def process_airdrop(self, user_id: str):
        # 0. Skip if custodian
        if user_id == settings.custodian_email:
            return {"status": "skipped", "reason": "Custodian account"}

        # 1. Check if user already got it

        if await self.reward_repo.has_received_airdrop(user_id):
            return {"status": "skipped", "reason": "Already received"}
            
        # 2. Check if limit reached
        count = await self.reward_repo.get_airdrop_count()
        if count >= settings.airdrop_limit:
            return {"status": "skipped", "reason": "Limit reached"}
            
        # 3. Perform transfer from custodian
        try:
            await self.reward_repo.transfer_reward(
                from_user_id=settings.custodian_email,
                to_user_id=user_id,
                amount=settings.airdrop_amount,
                reason="Early Adopter Airdrop"
            )
            return {"status": "success", "amount": settings.airdrop_amount}
        except Exception as e:
            return {"status": "error", "message": str(e)}

