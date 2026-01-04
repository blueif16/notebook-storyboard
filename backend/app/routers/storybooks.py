from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models import StoredAsset, Story
from app.controllers import storybook_controller

router = APIRouter()


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
