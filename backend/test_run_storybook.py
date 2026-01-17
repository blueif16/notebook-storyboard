"""实际运行故事书生成的测试脚本"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.storybook_gen import storybook_gen
from app.config import validate_config


async def main():
    """运行故事书生成测试"""
    print("🔍 检查配置...")
    if not validate_config():
        print("❌ 配置验证失败，请检查环境变量")
        return

    print("\n✅ 配置验证通过\n")

    # 测试故事
    story_text = """
    小兔子贝贝住在森林里的一个小木屋中。
    有一天，她决定去森林深处探险，寻找传说中的魔法蘑菇。
    在路上，她遇到了聪明的狐狸先生，他告诉贝贝魔法蘑菇的位置。
    最后，贝贝找到了魔法蘑菇，并用它帮助了生病的小鸟。
    """

    try:
        print("🚀 开始生成故事书...\n")
        result = await storybook_gen(story_text, aspect_ratio="16:9")

        print("\n" + "="*60)
        print("📊 生成结果统计")
        print("="*60)
        print(f"角色数量: {len(result.characters)}")
        for i, char in enumerate(result.characters, 1):
            print(f"  {i}. {char.name} - 图片ID: {char.image_id}")

        print(f"\n页面数量: {len(result.pages)}")
        for page in result.pages:
            print(f"  页面 {page.page_number}:")
            print(f"    情节: {page.plot[:50]}...")
            print(f"    角色: {', '.join(page.character_names)}")
            print(f"    参考页面: {page.reference_page_numbers}")
            print(f"    图片ID: {page.generated_image_id}")

        print("\n✅ 故事书生成成功！")

    except Exception as e:
        print(f"\n❌ 生成失败: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
