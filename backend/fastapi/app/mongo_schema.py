"""
DEPRECATED: This module has been moved to app.core.database.

This re-export exists only for backwards compatibility with any external
scripts that may import from here. Remove after confirming all consumers
have been updated.
"""

from app.core.database import ARTICLE_VALIDATOR, initialize_mongo_schema  # noqa: F401
