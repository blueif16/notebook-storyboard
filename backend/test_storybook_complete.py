"""完整的故事书生成测试脚本

测试内容：
1. 完整的storybook生成流程
2. 数据库存储验证
3. 链式图片生成验证
4. 图片URL获取验证
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.storybook_gen import storybook_gen
from app.services.storage_service import _init_supabase, get_image_url_from_asset_id
from app.config import SUPABASE_URL, SUPABASE_SECRET_KEY


async def verify_all_images_in_db(story):
    """验证所有图片都在数据库中"""
    print("\n" + "="*60)
    print("🔍 [验证] 检查所有图片是否存储到数据库")
    print("="*60)

    supabase = _init_supabase()
    if not supabase:
        print("❌ Supabase未初始化")
        return False

    all_valid = True

    # 验证角色图片
    print("\n📋 验证角色图片...")
    for i, char in enumerate(story.characters):
        print(f"  [{i+1}/{len(story.characters)}] 角色: {char.name}")
        print(f"    Image ID: {char.image_id}")
        print(f"    Image URL: {char.image_url[:50] if char.image_url else 'None'}...")

        try:
            response = (
                supabase.table("user_images")
                .select("id, storage_path, filename, file_size")
                .eq("id", char.image_id)
                .single()
                .execute()
            )
            if response.data:
                print(f"    ✅ 已存储: {response.data.get('filename')} ({response.data.get('file_size')} bytes)")
            else:
                print(f"    ❌ 未找到")
                all_valid = False
        except Exception as e:
            print(f"    ❌ 查询失败: {e}")
            all_valid = False

    # 验证页面图片
    print("\n📋 验证页面图片...")
    for page in story.pages:
        print(f"  [页面 {page.page_number}]")
        print(f"    Image ID: {page.generated_image_id}")
        print(f"    Image URL: {page.generated_image_url[:50] if page.generated_image_url else 'None'}...")

        try:
            response = (
                supabase.table("user_images")
                .select("id, storage_path, filename, file_size")
                .eq("id", page.generated_image_id)
                .single()
                .execute()
            )
            if response.data:
                print(f"    ✅ 已存储: {response.data.get('filename')} ({response.data.get('file_size')} bytes)")
            else:
                print(f"    ❌ 未找到")
                all_valid = False
        except Exception as e:
            print(f"    ❌ 查询失败: {e}")
            all_valid = False

    return all_valid


async def verify_image_urls(story):
    """验证可以获取所有图片的URL"""
    print("\n" + "="*60)
    print("🔗 [验证] 测试图片URL获取")
    print("="*60)

    all_valid = True

    # 测试角色图片URL
    print("\n📋 测试角色图片URL...")
    for i, char in enumerate(story.characters):
        print(f"  [{i+1}/{len(story.characters)}] 角色: {char.name}")
        url = await get_image_url_from_asset_id(char.image_id)
        if url:
            print(f"    ✅ URL获取成功 (长度: {len(url)})")
        else:
            print(f"    ❌ URL获取失败")
            all_valid = False

    # 测试页面图片URL
    print("\n📋 测试页面图片URL...")
    for page in story.pages:
        print(f"  [页面 {page.page_number}]")
        url = await get_image_url_from_asset_id(page.generated_image_id)
        if url:
            print(f"    ✅ URL获取成功 (长度: {len(url)})")
        else:
            print(f"    ❌ URL获取失败")
            all_valid = False

    return all_valid


async def verify_chain_generation(story):
    """验证链式生成逻辑"""
    print("\n" + "="*60)
    print("🔗 [验证] 检查链式图片生成")
    print("="*60)

    print("\n📋 分析每页的参考关系...")
    for page in story.pages:
        print(f"\n  [页面 {page.page_number}]")
        print(f"    情节: {page.plot[:80]}...")
        print(f"    涉及角色: {', '.join(page.character_names)}")
        print(f"    参考页面: {page.reference_page_numbers if page.reference_page_numbers else '无 (第一页)'}")

        # 计算实际使用的参考图片
        ref_count = len(page.character_names)
        if page.reference_page_numbers:
            ref_count += len(page.reference_page_numbers)

        print(f"    预期参考图片数: {ref_count}")
        print(f"    生成的图片ID: {page.generated_image_id}")

    return True


async def print_summary(story):
    """打印生成摘要"""
    print("\n" + "="*60)
    print("📊 [摘要] 故事书生成结果")
    print("="*60)

    print(f"\n✅ 角色数量: {len(story.characters)}")
    for i, char in enumerate(story.characters):
        print(f"  {i+1}. {char.name}")
        print(f"     ID: {char.image_id}")
        print(f"     URL: {char.image_url[:60] if char.image_url else 'None'}...")

    print(f"\n✅ 页面数量: {len(story.pages)}")
    for page in story.pages:
        print(f"  页面 {page.page_number}")
        print(f"     ID: {page.generated_image_id}")
        print(f"     URL: {page.generated_image_url[:60] if page.generated_image_url else 'None'}...")

    print(f"\n✅ 总图片数: {len(story.characters) + len(story.pages)}")


async def main():
    """主测试函数"""
    print("="*60)
    print("🚀 开始完整的故事书生成测试")
    print("="*60)

    # 检查配置
    print("\n📋 检查配置...")
    if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
        print("❌ Supabase配置缺失，请检查.env文件")
        return

    print(f"✅ Supabase URL: {SUPABASE_URL[:30]}...")
    print(f"✅ Supabase Key: {'*' * 20}")

    # 测试故事文本
    story_text = """
    小兔子莉莉住在森林里。有一天，她发现了一颗神奇的种子。
    她把种子种在花园里，第二天，种子长成了一棵巨大的彩虹树。
    树上结满了五颜六色的果实，每个果实都有不同的魔法。
    莉莉和她的朋友们一起分享了这些魔法果实，森林变得更加美丽了。
    """

    try:
        # 生成故事书
        print("\n" + "="*60)
        print("📚 [阶段1] 开始生成故事书")
        print("="*60)

        story = await storybook_gen(story_text, aspect_ratio="16:9")

        print("\n✅ 故事书生成完成！")

        # 验证数据库存储
        print("\n" + "="*60)
        print("📚 [阶段2] 验证数据库存储")
        print("="*60)

        db_valid = await verify_all_images_in_db(story)
        if db_valid:
            print("\n✅ 所有图片都已正确存储到数据库")
        else:
            print("\n❌ 部分图片未能正确存储")

        # 验证URL获取
        print("\n" + "="*60)
        print("📚 [阶段3] 验证URL获取")
        print("="*60)

        url_valid = await verify_image_urls(story)
        if url_valid:
            print("\n✅ 所有图片URL都可以正常获取")
        else:
            print("\n❌ 部分图片URL获取失败")

        # 验证链式生成
        print("\n" + "="*60)
        print("📚 [阶段4] 验证链式生成")
        print("="*60)

        await verify_chain_generation(story)

        # 打印摘要
        await print_summary(story)

        # 最终结果
        print("\n" + "="*60)
        if db_valid and url_valid:
            print("🎉 测试全部通过！")
        else:
            print("⚠️  测试部分失败，请检查上述错误")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

