"""
Tests for RewardService — the off-chain token reward system.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from app.services.reward_service import RewardService
from app.models.reward import UserReward


class TestClaimReadingReward:
    async def test_successful_claim(self, reward_service, mock_reward_repo, mock_article_repo):
        result = await reward_service.claim_reading_reward(
            user_id="user-001",
            article_id="test-article-001",
            read_time=30.0,
        )

        mock_article_repo.get_by_id.assert_called_once_with("test-article-001")
        mock_reward_repo.add_reward.assert_called_once()
        assert result["status"] == "claimed"

    async def test_rejects_insufficient_read_time(self, reward_service):
        with pytest.raises(HTTPException) as exc_info:
            await reward_service.claim_reading_reward(
                user_id="user-001",
                article_id="test-article-001",
                read_time=2.0,  # Below min_read_time (10s)
            )

        assert exc_info.value.status_code == 400
        assert "breve" in exc_info.value.detail.lower() or "mínimo" in exc_info.value.detail.lower()

    async def test_rejects_nonexistent_article(self, reward_service, mock_article_repo):
        mock_article_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await reward_service.claim_reading_reward(
                user_id="user-001",
                article_id="nonexistent",
                read_time=30.0,
            )

        assert exc_info.value.status_code == 404


class TestGetBalance:
    async def test_returns_balance(self, reward_service, mock_reward_repo):
        result = await reward_service.get_balance("user-001")

        mock_reward_repo.get_balance.assert_called_once_with("user-001")
        assert result["balance"] == 50.0
        assert result["userId"] == "user-001"

    async def test_returns_zero_for_new_user(self, reward_service, mock_reward_repo):
        mock_reward_repo.get_balance.return_value = UserReward(
            userId="new-user",
            totalBalance=0.0,
            transactions=[],
        )

        result = await reward_service.get_balance("new-user")
        assert result["balance"] == 0.0


class TestInitializeCustodian:
    async def test_initializes_with_default_amount(self, reward_service, mock_reward_repo):
        # Simulate custodian not yet initialized
        mock_reward_repo.get_balance.return_value = UserReward(
            userId="custodian",
            totalBalance=0.0,
            transactions=[],
        )

        result = await reward_service.initialize_custodian(amount=1000000.0)

        mock_reward_repo.add_reward.assert_called_once()
        assert result["status"] == "initialized"
        assert result["balance"] == 1000000.0

    async def test_skips_if_already_initialized(self, reward_service, mock_reward_repo):
        # Simulate custodian already initialized
        mock_reward_repo.get_balance.return_value = UserReward(
            userId="custodian",
            totalBalance=1000000.0,
            transactions=[],
        )

        result = await reward_service.initialize_custodian()

        mock_reward_repo.add_reward.assert_not_called()
        assert result["status"] == "already_initialized"


class TestAirdrop:
    async def test_skips_custodian_account(self, reward_service):
        result = await reward_service.process_airdrop("beysasj@gmail.com")

        assert result["status"] == "skipped"
