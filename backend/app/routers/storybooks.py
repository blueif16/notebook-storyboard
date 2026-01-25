from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel

from app.models import StoredAsset, Story, Character
from app.controllers import storybook_controller
from app.services.storybook_gen_modular import (
    generate_characters_only,
    generate_story_from_characters
)

# Agent-based generation
from app.graphs import run_storybook_generation

router = APIRouter()


# Request/Response models for new endpoints
class GenerateCharactersRequest(BaseModel):
    story_text: str
    style: str = "whimsical"


class GenerateCharactersResponse(BaseModel):
    story_id: str
    characters: List[Character]


class GenerateStoryRequest(BaseModel):
    story_id: str
    aspect_ratio: str = "16:9"


class GenerateStoryResponse(BaseModel):
    story: Story


@router.post("/generate-characters", response_model=GenerateCharactersResponse, status_code=status.HTTP_201_CREATED)
async def generate_characters(request: GenerateCharactersRequest):
    """Generate characters from story text (Phase 1)"""
    try:
        story_id, characters = await generate_characters_only(
            story_text=request.story_text,
            frontend_style=request.style
        )
        return GenerateCharactersResponse(
            story_id=story_id,
            characters=characters
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate characters: {str(e)}"
        )


@router.post("/generate-story", response_model=GenerateStoryResponse, status_code=status.HTTP_201_CREATED)
async def generate_story(request: GenerateStoryRequest):
    """Generate complete story from characters (Phase 2)"""
    try:
        story = await generate_story_from_characters(
            story_id=request.story_id,
            aspect_ratio=request.aspect_ratio
        )
        return GenerateStoryResponse(story=story)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate story: {str(e)}"
        )


@router.post("/", response_model=StoredAsset, status_code=status.HTTP_201_CREATED)
async def create_storybook(title: str, story: Story, source_titles: List[str] = None):
    """Create a new storybook"""
    try:
        return storybook_controller.create_storybook(title, story, source_titles)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create storybook: {str(e)}"
        )


@router.get("/", response_model=List[StoredAsset])
async def get_all_storybooks():
    """Get all storybooks"""
    try:
        return storybook_controller.get_all_storybooks()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve storybooks: {str(e)}"
        )


@router.get("/{storybook_id}", response_model=StoredAsset)
async def get_storybook(storybook_id: str):
    """Get a specific storybook by ID"""
    storybook = storybook_controller.get_storybook_by_id(storybook_id)
    if not storybook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Storybook with ID {storybook_id} not found"
        )
    return storybook


@router.delete("/{storybook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_storybook(storybook_id: str):
    """Delete a storybook by ID"""
    success = storybook_controller.delete_storybook(storybook_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Storybook with ID {storybook_id} not found"
        )


# ═══════════════════════════════════════════════════════════════════════
# AGENT-BASED GENERATION (New Architecture)
# ═══════════════════════════════════════════════════════════════════════

class AgentGenerateRequest(BaseModel):
    """Request for agent-based storybook generation."""
    story_text: str
    style: Optional[str] = "whimsical"
    page_count: Optional[int] = None


class AgentGenerateResponse(BaseModel):
    """Response from agent-based generation."""
    storybook_id: str
    title: str
    characters_count: int
    pages_count: int
    characters: List[dict]
    pages: List[dict]


@router.post("/agent-generate", response_model=AgentGenerateResponse)
async def agent_generate_storybook(request: AgentGenerateRequest):
    """
    Generate complete storybook using agent-based architecture.
    
    This is the NEW unified endpoint that replaces the 2-phase flow.
    Agents handle enhancement, character gen, page gen, and save automatically.
    
    Flow:
    1. Orchestrator enhances story and generates characters
    2. Story Generator creates illustrated pages sequentially
    3. Auto-saves to database
    
    Returns complete storybook data.
    """
    try:
        # Build user message with preferences
        user_message = request.story_text
        if request.style:
            user_message += f"\n\nStyle preference: {request.style}"
        if request.page_count:
            user_message += f"\n\nCreate {request.page_count} pages."
        
        # Run agent pipeline
        result = await run_storybook_generation(
            user_input=user_message,
            thread_id=None  # New conversation each time
        )
        
        # Extract results from state
        storybook_id = result.get("storybook_id")
        if not storybook_id:
            raise RuntimeError("Pipeline completed but no storybook_id found")
        
        return AgentGenerateResponse(
            storybook_id=storybook_id,
            title=result.get("title", "Untitled Story"),
            characters_count=len(result.get("characters", [])),
            pages_count=len(result.get("pages", [])),
            characters=result.get("characters", []),
            pages=result.get("pages", []),
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent-based generation failed: {str(e)}"
        )
