"""Story Tools for V2 Agent System

Functional tools only - no HITL tools here.
HITL tools moved to hitl_tools.py
"""
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool

from ..services.google_image_service import google_text_to_image, google_image_to_image
from ..services.storage_service import get_image_url_from_asset_id


# =============================================================================
# FUNCTIONAL TOOLS (External API calls)
# =============================================================================

@tool
async def generate_character_portrait(
    description: str,
    character_name: str = "",
    character_index: int = 0,

) -> Dict[str, str]:
    """
    Generate character portrait image, auto-saves to Supabase.

    Args:
        description: Detailed physical description of the character
        character_name: Name for reference
        character_index: Index in the characters array (0-based)

    Returns:
        Dict with name, image_id, image_url, and index
    """
    prompt = f"Character portrait: {description}. Studio lighting, white background, full body shot. No text, no distortions."

    image_id = await google_text_to_image(prompt=prompt, return_id=True)
    image_url = await get_image_url_from_asset_id(image_id)

    return {
        "name": character_name,
        "image_id": image_id,
        "image_url": image_url,
        "index": character_index
    }


@tool
async def generate_page_image(
    prompt: str, 
    reference_image_ids: List[str], 
    page_number: int = 0,
    aspect_ratio: Optional[str] = "16:9",
) -> Dict[str, str]:
    """
    Generate storybook page image with character/scene references.
    
    Args:
        prompt: Scene description for the page
        reference_image_ids: Character image IDs for visual consistency
        page_number: Page number in the storybook
        aspect_ratio: If story image, then default to use "16:9"
        
    Returns:
        Dict with image_id, image_url, and page_number
    """
    enhanced_prompt = f"{prompt}. Consistent style, professional composition. No text, no distortions, no watermarks."
    
    # Limit references to 14 (API constraint)
    if len(reference_image_ids) > 14:
        reference_image_ids = reference_image_ids[:14]
    
    if reference_image_ids:
        image_id = await google_image_to_image(
            prompt=enhanced_prompt, 
            image_asset_ids=reference_image_ids, 
            return_id=True,
            aspect_ratio=aspect_ratio
        
        )
    else:
        image_id = await google_text_to_image(
            prompt=enhanced_prompt, 
            return_id=True
        )
    
    image_url = await get_image_url_from_asset_id(image_id)
    
    return {
        "image_id": image_id, 
        "image_url": image_url, 
        "page_number": page_number
    }


@tool
async def save_storybook(
    title: str, 
    description: str, 
    pages: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Save complete storybook to database.
    
    Args:
        title: Storybook title
        description: Brief description
        pages: List of page dicts with image_id, image_url, page_number
        
    Returns:
        Dict with storybook_id, saved status, and page_count
    """
    from ..services.storage_service import _init_supabase
    import uuid
    from datetime import datetime
    
    supabase = _init_supabase()
    if not supabase:
        raise RuntimeError("Supabase not initialized")
    
    storybook_id = str(uuid.uuid4())
    
    supabase.table("storybooks").insert({
        "id": storybook_id,
        "title": title,
        "description": description,
        "pages": pages,
        "page_count": len(pages),
        "created_at": datetime.utcnow().isoformat(),
    }).execute()
    
    return {
        "storybook_id": storybook_id, 
        "saved": True, 
        "page_count": len(pages)
    }
