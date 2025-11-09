# This is a simple in-memory cache for the hackathon.
# It stores the text of the last uploaded PDF.

from typing import Dict, Optional, Any

# In-memory cache that can store any Python object (texts, event lists, etc.)
_cache: Dict[str, Any] = {}


def set(key: str, value: Any):
    """Stores a value in the cache."""
    _cache[key] = value


def get(key: str) -> Optional[Any]:
    """Retrieves a value from the cache."""
    return _cache.get(key)