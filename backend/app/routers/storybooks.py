from fastapi import APIRouter, HTTPException, status
from typing import List
from pydantic import BaseModel

from app.models import StoredAsset, Story, Character
from app.controllers import storybook_controller
from app.services.storybook_gen_modular import (
    generate_characters_only,
    generate_story_from_characters
)

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
