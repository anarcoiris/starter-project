import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

# Add the current directory to sys.path
sys.path.append(os.path.abspath(os.getcwd()))


from app.core.config import settings
from app.repositories.reward_repository import RewardRepository
from app.services.reward_service import RewardService
from app.repositories.article_repository import ArticleRepository

async def run_init():
    print(f"Connecting to MongoDB: {settings.mongodb_url}")
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    
    reward_repo = RewardRepository(db)
    article_repo = ArticleRepository(db) # Needed by service constructor
    service = RewardService(reward_repo, article_repo)
    
    print(f"Initializing custodian: {settings.custodian_email}")
    result = await service.initialize_custodian(amount=1000000.0)
    print(f"Result: {result}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(run_init())
