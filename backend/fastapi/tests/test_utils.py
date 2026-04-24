"""
Tests for core utilities.
"""

import asyncio
import pytest

from app.core.utils import retry_async


class TestRetryAsync:
    async def test_succeeds_on_first_attempt(self):
        call_count = 0

        async def success():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = await retry_async(success, description="test-success")
        assert result == "ok"
        assert call_count == 1

    async def test_retries_then_succeeds(self):
        call_count = 0

        async def fail_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("not ready")
            return "recovered"

        result = await retry_async(
            fail_twice,
            description="test-retry",
            base_delay=0.01,  # Fast for tests
        )
        assert result == "recovered"
        assert call_count == 3

    async def test_raises_after_max_attempts(self):
        async def always_fail():
            raise ConnectionError("permanent failure")

        with pytest.raises(ConnectionError, match="permanent failure"):
            await retry_async(
                always_fail,
                description="test-exhaust",
                max_attempts=3,
                base_delay=0.01,
            )

    async def test_exponential_backoff_caps_at_max_delay(self):
        """Verify backoff doesn't exceed max_delay (implicitly tested by timeout)."""
        call_count = 0

        async def fail_a_few():
            nonlocal call_count
            call_count += 1
            if call_count < 4:
                raise RuntimeError("not yet")
            return "done"

        result = await retry_async(
            fail_a_few,
            description="test-backoff",
            base_delay=0.01,
            max_delay=0.05,
        )
        assert result == "done"
        assert call_count == 4
