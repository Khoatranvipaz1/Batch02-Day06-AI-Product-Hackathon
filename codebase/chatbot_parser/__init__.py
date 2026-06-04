"""Parse ShopeeFood-style user messages into recommendation task JSON."""

from .parser import parse_user_query

__all__ = ["parse_user_query"]
