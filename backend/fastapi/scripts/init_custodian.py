import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.repositories.reward_repository import RewardRepository
from app.repositories.article_repository import ArticleRepository
from app.services.reward_service import RewardService

async def main():
    print(f"Initializing custodian: {settings.custodian_email}")
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    
    reward_repo = RewardRepository(db)
    article_repo = ArticleRepository(db) # Needed for service init
    
    reward_service = RewardService(reward_repo, article_repo)
    
    result = await reward_service.initialize_custodian(amount=1000000.0)
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
