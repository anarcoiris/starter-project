from fastapi import Request
from app.repositories.article_repository import ArticleRepository
from app.repositories.reward_repository import RewardRepository
from app.repositories.user_repository import UserRepository
from app.repositories.cache_repository import CacheRepository
from app.services.article_service import ArticleService
from app.services.ingestion_service import IngestionService
from app.services.reward_service import RewardService

def get_db(request: Request):
    return request.app.state.db

def get_article_repository(request: Request) -> ArticleRepository:
    return ArticleRepository(get_db(request))

def get_reward_repository(request: Request) -> RewardRepository:
    return RewardRepository(get_db(request))

def get_user_repository(request: Request) -> UserRepository:
    return UserRepository(get_db(request))

def get_cache_repository(request: Request) -> CacheRepository:
    return CacheRepository(get_db(request))

def get_article_service(request: Request) -> ArticleService:
    producer = getattr(request.app.state, 'producer', None)
    return ArticleService(get_article_repository(request), producer=producer)

def get_ingestion_service(request: Request) -> IngestionService:
    return IngestionService(
        get_article_repository(request), 
        get_cache_repository(request),
        producer=request.app.state.producer
    )

def get_reward_service(request: Request) -> RewardService:
    return RewardService(
        get_reward_repository(request),
        get_article_repository(request)
    )

