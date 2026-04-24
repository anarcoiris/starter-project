"""
Symmetry Platform — Test Suite

Shared fixtures for all test modules.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

import pytest

from app.models.article import Article, ArticleCreate
from app.models.reward import ClaimRequest, UserReward, RewardTransaction
from app.repositories.article_repository import ArticleRepository
from app.repositories.reward_repository import RewardRepository
from app.repositories.cache_repository import CacheRepository
from app.services.article_service import ArticleService
from app.services.reward_service import RewardService


# ── Sample Data ──────────────────────────────────────────────────────────────

SAMPLE_ARTICLE = Article(
    articleId="test-article-001",
    author="Test Author",
    title="Test Article Title",
    description="A test article for unit testing.",
    url="https://test.com/article-001",
    urlToImage="https://test.com/image.jpg",
    publishedAt=datetime(2026, 4, 24, tzinfo=timezone.utc),
    content="This is the content of the test article with enough words to test read time.",
    source="Test Source",
    category="technology",
    views=42,
    readTime=300,
    tokensEarned=10.0,
)

SAMPLE_ARTICLE_CREATE = ArticleCreate(
    author="Journalist Bot",
    title="Breaking News",
    description="Something happened.",
    url="https://test.com/breaking",
    urlToImage="https://test.com/breaking.jpg",
    content="This is the full content of the breaking news article for testing purposes.",
    source="Wire Service",
    category="general",
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_article_repo():
    repo = AsyncMock(spec=ArticleRepository)
    repo.get_all.return_value = [SAMPLE_ARTICLE]
    repo.get_by_id.return_value = SAMPLE_ARTICLE
    repo.create.return_value = SAMPLE_ARTICLE
    return repo


@pytest.fixture
def mock_reward_repo():
    repo = AsyncMock(spec=RewardRepository)
    repo.get_balance.return_value = UserReward(
        userId="user-001",
        totalBalance=50.0,
        transactions=[],
    )
    repo.add_reward.return_value = True
    return repo


@pytest.fixture
def mock_cache_repo():
    repo = AsyncMock(spec=CacheRepository)
    repo.get.return_value = None
    repo.set.return_value = None
    return repo


@pytest.fixture
def mock_producer():
    producer = AsyncMock()
    producer.send_and_wait.return_value = None
    return producer


@pytest.fixture
def article_service(mock_article_repo, mock_producer):
    return ArticleService(mock_article_repo, producer=mock_producer)


@pytest.fixture
def reward_service(mock_reward_repo, mock_article_repo):
    return RewardService(mock_reward_repo, mock_article_repo)
