"""
Tests for ArticleService — the core business logic for articles.
"""

import pytest
from unittest.mock import AsyncMock

from app.services.article_service import ArticleService
from app.models.article import ArticleRead
from tests.conftest import SAMPLE_ARTICLE, SAMPLE_ARTICLE_CREATE


class TestListArticles:
    async def test_returns_articles_from_repository(self, article_service, mock_article_repo):
        result = await article_service.list_latest_articles()
        
        mock_article_repo.get_all.assert_called_once_with(category=None, limit=10)
        assert len(result) == 1
        assert result[0].articleId == "test-article-001"

    async def test_passes_category_filter(self, article_service, mock_article_repo):
        await article_service.list_latest_articles(category="technology", limit=5)
        
        mock_article_repo.get_all.assert_called_once_with(category="technology", limit=5)


class TestCreateArticle:
    async def test_generates_article_id(self, article_service, mock_article_repo):
        await article_service.create_article(SAMPLE_ARTICLE_CREATE)
        
        # Verify create was called with an Article that has a generated ID
        mock_article_repo.create.assert_called_once()
        created_article = mock_article_repo.create.call_args[0][0]
        assert created_article.articleId is not None
        assert len(created_article.articleId) > 0

    async def test_calculates_expected_read_time(self, article_service, mock_article_repo):
        await article_service.create_article(SAMPLE_ARTICLE_CREATE)
        
        created_article = mock_article_repo.create.call_args[0][0]
        # Content has ~14 words → 0 minutes → minimum 10 seconds
        assert created_article.expectedReadTime >= 10

    async def test_sets_initial_counters_to_zero(self, article_service, mock_article_repo):
        await article_service.create_article(SAMPLE_ARTICLE_CREATE)
        
        created_article = mock_article_repo.create.call_args[0][0]
        assert created_article.views == 0
        assert created_article.tokensEarned == 0.0
        assert created_article.qualityScore == 1.0
        assert created_article.fraudScore == 0.0


class TestRegisterReadImpact:
    async def test_increments_read_metrics(self, article_service, mock_article_repo):
        event = ArticleRead(userId="user-001", readTimeSeconds=30)
        
        result = await article_service.register_read_impact("test-article-001", event)
        
        mock_article_repo.increment_read_metrics.assert_called_once_with("test-article-001", 30)
        assert result is True


class TestTriggerPdfGeneration:
    async def test_queues_task_to_kafka(self, article_service, mock_article_repo, mock_producer):
        result = await article_service.trigger_pdf_generation("test-article-001")
        
        mock_article_repo.get_by_id.assert_called_once_with("test-article-001")
        mock_producer.send_and_wait.assert_called_once()
        assert result is True

    async def test_returns_none_for_missing_article(self, article_service, mock_article_repo):
        mock_article_repo.get_by_id.return_value = None
        
        result = await article_service.trigger_pdf_generation("nonexistent-id")
        
        assert result is None

    async def test_returns_none_without_producer(self, mock_article_repo):
        service = ArticleService(mock_article_repo, producer=None)
        
        result = await service.trigger_pdf_generation("test-article-001")
        
        assert result is None
