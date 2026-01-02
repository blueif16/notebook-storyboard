from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models import StoredAsset, AssetCreate
from app.controllers import asset_controller

router = APIRouter()


@router.post("/", response_model=StoredAsset, status_code=status.HTTP_201_CREATED)
async def create_asset(asset_data: AssetCreate):
    """Create a new asset"""
    try:
        return asset_controller.create_asset(asset_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create asset: {str(e)}"
        )


@router.get("/", response_model=List[StoredAsset])
async def get_all_assets():
    """Get all assets"""
    try:
        return asset_controller.get_all_assets()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assets: {str(e)}"
        )


@router.get("/{asset_id}", response_model=StoredAsset)
async def get_asset(asset_id: str):
    """Get a specific asset by ID"""
    asset = asset_controller.get_asset_by_id(asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with ID {asset_id} not found"
        )
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: str):
    """Delete an asset by ID"""
    success = asset_controller.delete_asset(asset_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with ID {asset_id} not found"
        )


@router.get("/type/{asset_type}", response_model=List[StoredAsset])
async def get_assets_by_type(asset_type: str):
    """Get all assets of a specific type"""
    try:
        return asset_controller.get_assets_by_type(asset_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assets: {str(e)}"
        )
