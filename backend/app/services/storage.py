import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from app.models import StoredAsset, StoredStorybook, StoryPage, AssetMetadata


class StorageService:
    """Local file-based storage service for assets and storybooks"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.assets_file = self.data_dir / "assets.json"
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Ensure data directory and files exist"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.assets_file.exists():
            self._write_assets([])

    def _read_assets(self) -> list[dict]:
        """Read all assets from file"""
        try:
            with open(self.assets_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_assets(self, assets: list[dict]):
        """Write all assets to file"""
        with open(self.assets_file, 'w', encoding='utf-8') as f:
            json.dump(assets, f, indent=2, ensure_ascii=False)

    def save_asset(self, asset: StoredAsset) -> StoredAsset:
        """Save or update an asset"""
        assets = self._read_assets()

        # Remove existing asset with same ID
        assets = [a for a in assets if a.get('id') != asset.id]

        # Add new asset at the beginning
        assets.insert(0, asset.model_dump())

        self._write_assets(assets)
        return asset

    def get_all_assets(self) -> list[StoredAsset]:
        """Get all assets"""
        assets_data = self._read_assets()
        return [StoredAsset(**asset) for asset in assets_data]

    def get_asset_by_id(self, asset_id: str) -> Optional[StoredAsset]:
        """Get a specific asset by ID"""
        assets = self._read_assets()
        for asset_data in assets:
            if asset_data.get('id') == asset_id:
                return StoredAsset(**asset_data)
        return None

    def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset by ID"""
        assets = self._read_assets()
        filtered = [a for a in assets if a.get('id') != asset_id]

        if len(filtered) == len(assets):
            return False  # Asset not found

        self._write_assets(filtered)
        return True

    def get_assets_by_type(self, asset_type: str) -> list[StoredAsset]:
        """Get all assets of a specific type"""
        assets = self.get_all_assets()
        return [a for a in assets if a.type == asset_type]

    def save_storybook(
        self,
        title: str,
        pages: list[StoryPage],
        source_titles: list[str] = None
    ) -> StoredStorybook:
        """Save a storybook and return it"""
        if source_titles is None:
            source_titles = []

        storybook = StoredStorybook(
            id=f"storybook-{int(datetime.now().timestamp() * 1000)}",
            title=title,
            pages=pages,
            createdAt=int(datetime.now().timestamp() * 1000),
            sourceCount=len(source_titles),
            sourceTitles=source_titles
        )

        # Save as generic asset
        asset = StoredAsset(
            id=storybook.id,
            type="storybook",
            title=storybook.title,
            createdAt=storybook.createdAt,
            data=storybook.model_dump(),
            metadata=AssetMetadata(
                sourceCount=storybook.sourceCount,
                sourceTitles=storybook.sourceTitles
            )
        )

        self.save_asset(asset)
        return storybook

    def get_all_storybooks(self) -> list[StoredStorybook]:
        """Get all storybooks"""
        assets = self.get_assets_by_type("storybook")
        return [StoredStorybook(**asset.data) for asset in assets]

    def get_storybook_by_id(self, storybook_id: str) -> Optional[StoredStorybook]:
        """Get a specific storybook by ID"""
        asset = self.get_asset_by_id(storybook_id)
        if asset and asset.type == "storybook":
            return StoredStorybook(**asset.data)
        return None


# Singleton instance
storage_service = StorageService()
