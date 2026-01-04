from pydantic import BaseModel, Field
from typing import Optional, Any, Literal
from .story import Story


class AssetMetadata(BaseModel):
    sourceCount: Optional[int] = None
    sourceTitles: Optional[list[str]] = None


class StoredAsset(BaseModel):
    id: str
    type: Literal["storybook", "slides", "mindmap", "audio", "summary"]
    title: str
    createdAt: int
    data: Any
    metadata: Optional[AssetMetadata] = None


class AssetCreate(BaseModel):
    type: Literal["storybook", "slides", "mindmap", "audio", "summary"]
    title: str
    data: Any
    metadata: Optional[AssetMetadata] = None
