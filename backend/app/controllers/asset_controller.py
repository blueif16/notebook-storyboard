from typing import Optional
from datetime import datetime

from app.models import (
    StoredAsset,
    StoredStorybook,
    AssetCreate,
    StorybookCreate,
    StoryPage,
    AssetMetadata
)
from app.services import storage_service


class AssetController:
    """Controller for asset operations"""

    def __init__(self):
        self.storage = storage_service

    def create_asset(self, asset_data: AssetCreate) -> StoredAsset:
        """Create a new asset"""
        asset = StoredAsset(
            id=f"{asset_data.type}-{int(datetime.now().timestamp() * 1000)}",
            type=asset_data.type,
            title=asset_data.title,
            createdAt=int(datetime.now().timestamp() * 1000),
            data=asset_data.data,
            metadata=asset_data.metadata
        )
        return self.storage.save_asset(asset)

    def get_all_assets(self) -> list[StoredAsset]:
        """Get all assets"""
        return self.storage.get_all_assets()

    def get_asset_by_id(self, asset_id: str) -> Optional[StoredAsset]:
        """Get asset by ID"""
        return self.storage.get_asset_by_id(asset_id)

    def delete_asset(self, asset_id: str) -> bool:
        """Delete asset by ID"""
        return self.storage.delete_asset(asset_id)

    def get_assets_by_type(self, asset_type: str) -> list[StoredAsset]:
        """Get assets by type"""
        return self.storage.get_assets_by_type(asset_type)


class StorybookController:
    """Controller for storybook operations"""

    def __init__(self):
        self.storage = storage_service

    def create_storybook(self, storybook_data: StorybookCreate) -> StoredStorybook:
        """Create a new storybook"""
        return self.storage.save_storybook(
            title=storybook_data.title,
            pages=storybook_data.pages,
            source_titles=storybook_data.sourceTitles
        )

    def get_all_storybooks(self) -> list[StoredStorybook]:
        """Get all storybooks"""
        return self.storage.get_all_storybooks()

    def get_storybook_by_id(self, storybook_id: str) -> Optional[StoredStorybook]:
        """Get storybook by ID"""
        return self.storage.get_storybook_by_id(storybook_id)

    def delete_storybook(self, storybook_id: str) -> bool:
        """Delete storybook by ID"""
        return self.storage.delete_asset(storybook_id)


# Singleton instances
asset_controller = AssetController()
storybook_controller = StorybookController()
