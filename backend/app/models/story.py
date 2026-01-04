from pydantic import BaseModel
from typing import List, Optional


class Character(BaseModel):
    """角色信息"""
    name: str
    description: str
    image_id: Optional[str] = None


class StoryPage(BaseModel):
    """故事页面"""
    page_number: int
    plot: str
    character_names: List[str]
    reference_page_numbers: List[int]
    generated_image_id: Optional[str] = None


class Story(BaseModel):
    """故事脚本"""
    characters: List[Character]
    pages: List[StoryPage]
