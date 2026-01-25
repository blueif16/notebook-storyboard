"""故事书生成服务 - 链式参考图像生成"""
import instructor
from pydantic import BaseModel
from typing import List
from datetime import datetime
from ..config import GOOGLE_API_KEY, GEMINI_TEXT_MODEL
from .google_image_service import google_text_to_image, google_image_to_image
from .storage_service import _init_supabase, get_image_url_from_asset_id
from .story_storage import StoryStorage, generate_story_id
from ..models import Character, Story

# Style configurations with English keys and descriptive prompt text
STYLE_CONFIGS = {
    "cinematic": "Photorealistic, shot on 35mm film, cinematic color grading with subtle warmth, natural skin texture, sharp focus, shallow depth of field, dramatic lighting",
    "anime": "Vibrant anime style, cel shading, bold clean outlines, dynamic composition, saturated colors, expressive character design",
    "watercolor": "Watercolor illustration, soft bleeding edges, visible paper texture, gentle color washes, muted tones, hand-painted brush strokes",
    "3d_render": "High-quality 3D render, Pixar-style aesthetic, soft studio lighting, clean materials, ultra-detailed surfaces, smooth shading"
}


async def _verify_image_in_db(asset_id: str) -> bool:
    """验证图片是否成功存储到数据库

    Args:
        asset_id: 图片的asset_id

    Returns:
        bool: 是否存在于数据库中
    """
    if not asset_id:
        return False

    supabase = _init_supabase()
    if not supabase:
        print("⚠️  [DB_VERIFY] Supabase未初始化")
        return False

    try:
        response = (
            supabase.table("user_images")
            .select("id, storage_path, filename")
            .eq("id", asset_id)
            .single()
            .execute()
        )
        if response.data:
            print(f"✅ [DB_VERIFY] 图片已存储: {response.data.get('filename')}")
            return True
        else:
            print(f"❌ [DB_VERIFY] 图片不存在: {asset_id}")
            return False
    except Exception as e:
        print(f"❌ [DB_VERIFY] 验证失败: {e}")
        return False


async def storybook_gen(
    story_text: str,
    aspect_ratio: str = "16:9",
    style: str = "cinematic"  # cinematic | anime | watercolor | 3d_render
) -> Story:
    """完整的故事书生成流程

    Args:
        story_text: 用户输入的故事文本
        aspect_ratio: 图片宽高比，默认 "16:9"
        style: 图片风格，可选 "cinematic" | "anime" | "watercolor" | "3d_render"

    Returns:
        Story: 完整的故事脚本（所有图片已生成）
    """
    print(f"\n{'='*60}")
    print("📚 [STORYBOOK_GEN] 故事书生成开始")
    print(f"📋 故事文本长度: {len(story_text)} 字符")
    print(f"📋 图片比例: {aspect_ratio}")
    print(f"🎨 图片风格: {style}")
    print(f"{'='*60}\n")

    # 生成故事ID并创建文件夹结构
    story_id = generate_story_id()
    storage = StoryStorage(story_id)
    storage.create_structure()
    print(f"📁 故事ID: {story_id}")

    # 初始化 Instructor 客户端
    client = instructor.from_provider(
        f"google/{GEMINI_TEXT_MODEL}",
        api_key=GOOGLE_API_KEY
    )

    # 阶段0：故事扩充
    print("📝 [阶段0] 故事扩充...")
    from google import genai
    from google.genai import types

    gemini_client = genai.Client(api_key=GOOGLE_API_KEY)

    enhanced_response = gemini_client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        config=types.GenerateContentConfig(
            system_instruction="""故事书编剧。为图像生成优化故事结构：

            1. 角色首次出场时描述一次外貌特征，后续不再重复
            2. 每个新场景需描述：地点、时间、光线、环境氛围
            3. 相同场景复现时无需重复描述
            4. 保留角色动作、表情、互动细节

            若场景描述缺失或模糊，补充具体视觉细节。仅输出故事，无解释。""" ),
        contents=f"故事内容：\n{story_text}"
    )
    story_text = enhanced_response.text
    print(f"✅ 故事处理完成，长度: {len(story_text)} 字符")

    # 阶段1：提取角色信息
    print("\n🎭 [阶段1] 提取角色信息...")
    class CharacterList(BaseModel):
        characters: List[Character]

    character_result = client.chat.completions.create(
        response_model=CharacterList,
        messages=[{
            "role": "user",
            "content": f"从以下故事中提取所有主要角色，包括名字和详细的外貌描述：\n\n{story_text}"
        }]
    )
    characters = character_result.characters
    print(f"✅ 提取到 {len(characters)} 个角色")

    # 阶段2：生成角色图片
    print("\n🎨 [阶段2] 生成角色图片...")
    for i, char in enumerate(characters):
        print(f"  [{i+1}/{len(characters)}] 生成角色: {char.name}")
        prompt = f"Character portrait: {char.name}. {char.description}. Studio lighting, white background, full body shot."

        # 准备本地保存路径
        local_path = storage.characters_folder / f"character_{i+1:02d}_{char.name}.jpg"

        # 生成图片并保存到本地和Supabase
        char.image_id = await google_text_to_image(
            prompt,
            return_id=True,
            local_save_path=str(local_path)
        )
        print(f"  📋 角色图片ID: {char.image_id}")

        # 验证图片是否成功存储到数据库
        if not await _verify_image_in_db(char.image_id):
            raise RuntimeError(
                f"角色 {char.name} 的图片未能成功存储到数据库 (ID: {char.image_id})"
            )
        print(f"  ✅ 角色图片已验证并存储到数据库")

        # 获取图片URL
        char.image_url = await get_image_url_from_asset_id(char.image_id)
        print(f"  🔗 角色图片URL: {char.image_url[:50] if char.image_url else 'None'}...")

    # 阶段3：生成故事脚本
    print("\n📖 [阶段3] 生成故事脚本...")
    character_names = [c.name for c in characters]

    script_result = client.chat.completions.create(
        response_model=Story,
        messages=[{
            "role": "user",
            "content": f"""将以下故事分解为多个页面，根据故事内容合理决定需要多少幅图片来呈现。每页包含：
1. page_number: 页码（从1开始）
2. plot: 该页的故事情节描述
3. character_names: 该页出现的角色名字列表（从这些角色中选择：{character_names}）
4. reference_page_numbers: 需要引用的之前页面的页码列表（第1页为空列表，后续页面可以引用之前的页面）

故事内容：
{story_text}"""
        }]
    )

    # 将生成的角色信息填充到脚本中
    script_result.characters = characters
    print(f"✅ 生成 {len(script_result.pages)} 页故事脚本")

    # 阶段4：按顺序生成每页图片
    print("\n🖼️  [阶段4] 生成故事页面图片...")
    for page in script_result.pages:
        print(f"\n  📄 [页面 {page.page_number}] 开始生成...")

        # 优化 plot 为图片生成 prompt
        optimized_prompt = await _optimize_plot_for_image(page.plot, page.character_names, style)
        print(f"  📝 优化后的prompt: {optimized_prompt[:100]}...")

        # 收集参考图片ID
        reference_ids = []

        # 添加角色图片
        print(f"  🎭 收集角色参考图片...")
        for char_name in page.character_names:
            char = next((c for c in characters if c.name == char_name), None)
            if char and char.image_id:
                reference_ids.append(char.image_id)
                print(f"    - 角色 {char_name}: {char.image_id}")

        # 添加之前页面的图片
        if page.reference_page_numbers:
            print(f"  🔗 收集之前页面的参考图片...")
            for ref_page_num in page.reference_page_numbers:
                ref_page = next((p for p in script_result.pages if p.page_number == ref_page_num), None)
                if ref_page and ref_page.generated_image_id:
                    reference_ids.append(ref_page.generated_image_id)
                    print(f"    - 页面 {ref_page_num}: {ref_page.generated_image_id}")

        print(f"  📊 总参考图片数量: {len(reference_ids)}")

        # 准备本地保存路径
        local_path = storage.pages_folder / f"page_{page.page_number:02d}.jpg"

        # 生成图片
        if reference_ids:
            print(f"  🎨 使用图生图模式 (参考 {len(reference_ids)} 张图片)...")
            page.generated_image_id = await google_image_to_image(
                prompt=optimized_prompt,
                image_asset_ids=reference_ids,
                aspect_ratio=aspect_ratio,
                return_id=True,
                local_save_path=str(local_path)
            )
        else:
            # 第一页没有参考图，使用文生图
            print(f"  🎨 使用文生图模式 (第一页)...")
            page.generated_image_id = await google_text_to_image(
                prompt=optimized_prompt,
                return_id=True,
                local_save_path=str(local_path)
            )

        print(f"  📋 页面图片ID: {page.generated_image_id}")

        # 验证图片是否成功存储到数据库
        if not await _verify_image_in_db(page.generated_image_id):
            raise RuntimeError(
                f"页面 {page.page_number} 的图片未能成功存储到数据库 (ID: {page.generated_image_id})"
            )
        print(f"  ✅ 页面图片已验证并存储到数据库")

        # 获取图片URL
        page.generated_image_url = await get_image_url_from_asset_id(page.generated_image_id)
        print(f"  🔗 页面图片URL: {page.generated_image_url[:50] if page.generated_image_url else 'None'}...")

    # 设置故事ID
    script_result.story_id = story_id

    # 保存元数据
    metadata = {
        "story_id": story_id,
        "created_at": datetime.now().isoformat(),
        "total_characters": len(script_result.characters),
        "total_pages": len(script_result.pages),
        "aspect_ratio": aspect_ratio
    }
    storage.save_metadata(metadata)

    # 保存完整故事JSON
    storage.save_story_json(script_result.model_dump())

    print(f"\n{'='*60}")
    print("🎉 [STORYBOOK_GEN] 故事书生成完成！")
    print(f"✅ 故事ID: {story_id}")
    print(f"✅ 角色数量: {len(script_result.characters)}")
    print(f"✅ 页面数量: {len(script_result.pages)}")
    print(f"✅ 本地文件夹: {storage.story_folder}")
    print(f"{'='*60}\n")

    return script_result


async def _optimize_plot_for_image(
    plot: str,
    character_names: List[str],
    style: str = "anime"  # cinematic | anime | watercolor | 3d_render
) -> str:
    """优化故事情节为图片生成 prompt"""
    from google import genai
    from google.genai import types

    gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
    style_text = STYLE_CONFIGS.get(style, STYLE_CONFIGS["cinematic"])

    response = gemini_client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=f"""Convert story plot into Nano Banana image prompt. Output in English only.

FORMAT (under 150 words, single paragraph):
[Subject: character appearance + pose/expression] + [Setting: environment + time/weather] + [Composition: camera angle + framing] + [Lighting: light source + mood] + [Style: {style_text}]

RULES:
- Describe FINAL STATIC STATE only, never processes or motion
- Replace character names with specific visual traits (hair color, clothing, age)
- Use concrete visual details, not abstract concepts
- Include: No distorted limbs, no extra fingers, no text, no watermarks

BAD: "A woman is opening a gift box excitedly"
GOOD: "A young woman with long black hair, hands lifting an open white gift box, joyful expression, eyes wide with delight"

Output the prompt directly, no explanation."""
        ),
        contents=f"""Story: {plot}
Characters: {', '.join(character_names)}"""
    )

    return response.text

