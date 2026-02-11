"""Style Catalog Service - Fetch pre-baked styles from Supabase"""
import logging
from typing import Optional, Any

from ..config import SUPABASE_URL, SUPABASE_SECRET_KEY

logger = logging.getLogger(__name__)

_supabase: Optional[Any] = None
_supabase_initialized = False


def _init_supabase():
    global _supabase, _supabase_initialized
    if _supabase_initialized:
        return _supabase
    try:
        from supabase import create_client
        if SUPABASE_URL and SUPABASE_SECRET_KEY:
            _supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
        _supabase_initialized = True
    except ImportError:
        logger.warning("Supabase not available")
    except Exception as e:
        logger.warning(f"Supabase initialization failed: {e}")
    return _supabase


async def get_all_styles() -> list[dict]:
    """Fetch all active styles ordered by sort_order."""
    client = _init_supabase()
    if not client:
        logger.error("[STYLE CATALOG] No Supabase client")
        return []

    response = (
        client.table("style_catalog")
        .select("key, name, description, image_url")
        .eq("active", True)
        .order("sort_order")
        .execute()
    )
    return response.data or []


async def get_styles_by_keys(keys: list[str]) -> list[dict]:
    """Fetch specific styles by their keys, preserving key order."""
    client = _init_supabase()
    if not client:
        logger.error("[STYLE CATALOG] No Supabase client")
        return []

    response = (
        client.table("style_catalog")
        .select("key, name, description, image_url")
        .in_("key", keys)
        .eq("active", True)
        .execute()
    )
    rows = response.data or []

    # Preserve the order the agent requested
    by_key = {r["key"]: r for r in rows}
    return [by_key[k] for k in keys if k in by_key]
