from pydantic import BaseModel, Field
from typing import Optional, Any, Literal
from datetime import datetime


class StoryPage(BaseModel):
    leftImage: Optional[str] = None
    rightImage: Optional[str] = None
    leftText: Optional[str] = None
    rightText: Optional[str] = None
    imagePrompt: Optional[str] = None


class StoredStorybook(BaseModel):
    id: str
    title: str
    pages: list[StoryPage]
    createdAt: int
    sourceCount: int
    sourceTitles: list[str]


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


class StorybookCreate(BaseModel):
    title: str
    pages: list[StoryPage]
    sourceTitles: list[str] = Field(default_factory=list)
