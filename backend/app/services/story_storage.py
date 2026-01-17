"""故事本地存储管理"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from ..config import BASE_DIR


class StoryStorage:
    """管理故事的本地文件夹结构"""

    def __init__(self, story_id: str):
        """初始化故事存储

        Args:
            story_id: 故事唯一ID（格式：story_20260105_123456）
        """
        self.story_id = story_id
        self.base_dir = Path(__file__).parent.parent.parent / BASE_DIR
        self.story_folder = self.base_dir / "stories" / story_id

        # 子文件夹
        self.characters_folder = self.story_folder / "characters"
        self.pages_folder = self.story_folder / "pages"

    def create_structure(self):
        """创建故事文件夹结构"""
        self.story_folder.mkdir(parents=True, exist_ok=True)
        self.characters_folder.mkdir(exist_ok=True)
        self.pages_folder.mkdir(exist_ok=True)
        print(f"📁 创建故事文件夹: {self.story_folder}")

    def save_character_image(self, character_name: str, image_data: bytes,
                            character_index: int) -> str:
        """保存角色图片

        Args:
            character_name: 角色名字
            image_data: 图片二进制数据
            character_index: 角色索引（从1开始）

        Returns:
            str: 保存的文件路径
        """
        filename = f"character_{character_index:02d}_{character_name}.jpg"
        filepath = self.characters_folder / filename

        with open(filepath, "wb") as f:
            f.write(image_data)

        print(f"💾 保存角色图片: {filepath}")
        return str(filepath)

    def save_page_image(self, page_number: int, image_data: bytes) -> str:
        """保存页面图片

        Args:
            page_number: 页码
            image_data: 图片二进制数据

        Returns:
            str: 保存的文件路径
        """
        filename = f"page_{page_number:02d}.jpg"
        filepath = self.pages_folder / filename

        with open(filepath, "wb") as f:
            f.write(image_data)

        print(f"💾 保存页面图片: {filepath}")
        return str(filepath)

    def save_metadata(self, metadata: dict):
        """保存故事元数据

        Args:
            metadata: 元数据字典（包含标题、创建时间等）
        """
        filepath = self.story_folder / "metadata.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"💾 保存元数据: {filepath}")

    def save_story_json(self, story_data: dict):
        """保存完整故事数据

        Args:
            story_data: 故事完整数据（Story模型的dict）
        """
        filepath = self.story_folder / "story.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(story_data, f, ensure_ascii=False, indent=2)
        print(f"💾 保存故事数据: {filepath}")


def generate_story_id() -> str:
    """生成故事唯一ID

    Returns:
        str: 格式为 story_20260105_123456
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"story_{timestamp}"

