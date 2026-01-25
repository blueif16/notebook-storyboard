"""Story Tools for Agent-Based Storybook Generation"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.types import interrupt
import instructor

from ..config import GOOGLE_API_KEY, GEMINI_TEXT_MODEL
from ..services.google_image_service import google_text_to_image, google_image_to_image
from ..services.storage_service import get_image_url_from_asset_id


@tool
async def enhance_and_extract(story_text: str) -> Dict[str, Any]:
    """Enhance story for visual generation and extract characters."""
    client = instructor.from_provider(f"google/{GEMINI_TEXT_MODEL}", api_key=GOOGLE_API_KEY)
    
    class CharacterInfo(BaseModel):
        name: str
        description: str = Field(description="Detailed physical description")
    
    class Result(BaseModel):
        enhanced_story: str
        characters: List[CharacterInfo]
    
    result = client.chat.completions.create(
        response_model=Result,
        messages=[{
            "role": "user",
            "content": f"""Enhance this story for illustration and extract characters:

{story_text}

Tasks:
1. enhanced_story: Add visual details (character appearances, scene descriptions, settings)
2. characters: Extract all characters with detailed physical descriptions

Output in English."""
        }]
    )
    
    return {
        "enhanced_story": result.enhanced_story,
        "characters": [{"name": c.name, "description": c.description} for c in result.characters]
    }


@tool
async def generate_character_portrait(description: str, character_name: str = "") -> Dict[str, str]:
    """Generate character portrait, auto-saves to Supabase."""
    prompt = f"Character portrait: {description}. Studio lighting, white background, full body shot. No text, no distortions."
    
    image_id = await google_text_to_image(prompt=prompt, return_id=True)
    image_url = await get_image_url_from_asset_id(image_id)
    
    return {"image_id": image_id, "image_url": image_url}


@tool
async def generate_page_image(prompt: str, reference_image_ids: List[str], page_number: int = 0) -> Dict[str, str]:
    """Generate storybook page with references, auto-saves to Supabase."""
    enhanced_prompt = f"{prompt}. Consistent style, professional composition. No text, no distortions, no watermarks."
    
    if len(reference_image_ids) > 14:
        reference_image_ids = reference_image_ids[:14]
    
    if reference_image_ids:
        image_id = await google_image_to_image(prompt=enhanced_prompt, image_asset_ids=reference_image_ids, return_id=True)
    else:
        image_id = await google_text_to_image(prompt=enhanced_prompt, return_id=True)
    
    image_url = await get_image_url_from_asset_id(image_id)
    
    return {"image_id": image_id, "image_url": image_url}


@tool
async def save_storybook(title: str, description: str, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Save complete storybook to database."""
    from ..services.storage_service import _init_supabase
    import uuid
    from datetime import datetime
    
    supabase = _init_supabase()
    if not supabase:
        raise RuntimeError("Supabase not initialized")
    
    storybook_id = str(uuid.uuid4())
    
    result = supabase.table("storybooks").insert({
        "id": storybook_id,
        "title": title,
        "description": description,
        "pages": pages,
        "page_count": len(pages),
        "created_at": datetime.utcnow().isoformat(),
    }).execute()
    
    return {"storybook_id": storybook_id, "saved": True, "page_count": len(pages)}


@tool
def request_user_input(question: str, images: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """Request input from user with optional image display."""
    response = interrupt({"type": "user_input", "question": question, "images": images or []})
    return response


ORCHESTRATOR_TOOLS = [enhance_and_extract, generate_character_portrait, request_user_input]
STORY_GENERATOR_TOOLS = [generate_page_image, save_storybook, request_user_input]
ALL_STORY_TOOLS = [enhance_and_extract, generate_character_portrait, generate_page_image, save_storybook, request_user_input]
