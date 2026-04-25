"""
Symmetry Platform — Shared Utilities

Reusable patterns for workers and services.
"""

import asyncio
import logging
from functools import wraps
from typing import Callable, Optional

logger = logging.getLogger(__name__)


async def retry_async(
    coro_func: Callable,
    *args,
    max_attempts: int = 20,
    base_delay: float = 2.0,
    max_delay: float = 60.0,
    description: str = "operation",
    **kwargs,
):
    """
    Retry an async coroutine with exponential backoff.

    Args:
        coro_func: The async function to call.
        max_attempts: Maximum number of retry attempts (0 = infinite).
        base_delay: Initial delay in seconds between retries.
        max_delay: Maximum delay cap in seconds.
        description: Human-readable label for log messages.
    """
    attempt = 0
    while True:
        try:
            return await coro_func(*args, **kwargs)
        except Exception as e:
            attempt += 1
            if max_attempts and attempt >= max_attempts:
                logger.error(
                    f"[{description}] Failed after {attempt} attempts: {e}"
                )
                raise
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            logger.warning(
                f"[{description}] Attempt {attempt} failed: {e}. "
                f"Retrying in {delay:.1f}s..."
            )
            await asyncio.sleep(delay)
