from app.repositories.reward_repository import RewardRepository
from app.repositories.article_repository import ArticleRepository
from fastapi import HTTPException

class RewardService:
    def __init__(self, reward_repo: RewardRepository, article_repo: ArticleRepository):
        self.reward_repo = reward_repo
        self.article_repo = article_repo

    async def claim_reading_reward(self, user_id: str, article_id: str, read_time: float = 0.0):
        # 1. Check if article exists
        article = await self.article_repo.get_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")

        # 2. Basic Scoring Layer: Minimum read time (e.g. 10 seconds for alpha)
        MIN_READ_TIME = 10.0
        if read_time < MIN_READ_TIME:
            import logging
            logging.warning(f"Recompensa rechazada para {user_id}: tiempo insuficiente ({read_time}s)")
            raise HTTPException(
                status_code=400, 
                detail=f"Lectura demasiado breve para recompensa. Mínimo: {MIN_READ_TIME}s"
            )

        # 3. Check if already claimed for this article
        user_reward = await self.reward_repo.get_user_reward(user_id)
        for tx in user_reward.transactions:
            if tx.referenceId == article_id and tx.reason == "Article Read":
                raise HTTPException(status_code=400, detail="Reward already claimed for this article")

        # 4. Apply reward
        reward_amount = 5.0
        return await self.reward_repo.add_reward(
            user_id=user_id,
            amount=reward_amount,
            reason="Article Read",
            reference_id=article_id
        )


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
        from app.core.config import settings
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
        from app.core.config import settings
        
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

