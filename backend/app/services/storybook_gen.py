"""故事书生成服务 - 链式参考图像生成"""
import instructor
from pydantic import BaseModel
from typing import List, Any
from ..config import GOOGLE_API_KEY
from .google_image_service import google_text_to_image, google_image_to_image
from ..models import Character, Story


async def storybook_gen(
    story_text: str,
    aspect_ratio: str = "16:9"
) -> Story:
    """完整的故事书生成流程

    Args:
        story_text: 用户输入的故事文本
        aspect_ratio: 图片宽高比，默认 "16:9"

    Returns:
        Story: 完整的故事脚本（所有图片已生成）
    """
    print(f"\n{'='*60}")
    print("📚 [STORYBOOK_GEN] 故事书生成开始")
    print(f"📋 故事文本长度: {len(story_text)} 字符")
    print(f"📋 图片比例: {aspect_ratio}")
    print(f"{'='*60}\n")

    # 初始化 Instructor 客户端
    client = instructor.from_provider(
        "google/gemini-3-flash-preview",
        api_key=GOOGLE_API_KEY
    )

    # 阶段0：故事扩充
    print("📝 [阶段0] 故事扩充...")
    class EnhancedStory(BaseModel):
        story: str

    enhanced_result = client.chat.completions.create(
        response_model=EnhancedStory,
        messages=[{
            "role": "user",
            "content": f"""分析以下故事，如果故事已经完善完整（人物、情节、细节都清晰），则原封不动返回。如果故事不完整或缺少细节，请填充必要的细节，把人物、场景、情节讲清楚。

故事内容：
{story_text}"""
        }]
    )
    story_text = enhanced_result.story
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
        char.image_id = await google_text_to_image(prompt, return_id=True)
        print(f"  ✅ 角色图片ID: {char.image_id}")

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
        optimized_prompt = await _optimize_plot_for_image(client, page.plot, page.character_names)
        print(f"  📝 优化后的prompt: {optimized_prompt[:100]}...")

        # 收集参考图片ID
        reference_ids = []

        # 添加角色图片
        for char_name in page.character_names:
            char = next((c for c in characters if c.name == char_name), None)
            if char and char.image_id:
                reference_ids.append(char.image_id)

        # 添加之前页面的图片
        for ref_page_num in page.reference_page_numbers:
            ref_page = next((p for p in script_result.pages if p.page_number == ref_page_num), None)
            if ref_page and ref_page.generated_image_id:
                reference_ids.append(ref_page.generated_image_id)

        print(f"  🔗 参考图片数量: {len(reference_ids)}")

        # 生成图片
        if reference_ids:
            page.generated_image_id = await google_image_to_image(
                prompt=optimized_prompt,
                image_asset_ids=reference_ids,
                aspect_ratio=aspect_ratio,
                return_id=True
            )
        else:
            # 第一页没有参考图，使用文生图
            page.generated_image_id = await google_text_to_image(
                prompt=optimized_prompt,
                return_id=True
            )

        print(f"  ✅ 页面图片ID: {page.generated_image_id}")

    print(f"\n{'='*60}")
    print("🎉 [STORYBOOK_GEN] 故事书生成完成！")
    print(f"✅ 角色数量: {len(script_result.characters)}")
    print(f"✅ 页面数量: {len(script_result.pages)}")
    print(f"{'='*60}\n")

    return script_result


async def _optimize_plot_for_image(
    client: Any,
    plot: str,
    character_names: List[str]
) -> str:
    """优化故事情节为图片生成 prompt"""
    response = client.chat.completions.create(
        model="gemini-3-flash-preview",
        messages=[{
            "role": "user",
            "content": f"""将以下故事情节转换为详细的视觉场景描述，适合用于图片生成。
包含场景、角色动作、环境细节、光线氛围等。

故事情节：{plot}
涉及角色：{', '.join(character_names)}

请直接输出优化后的场景描述，不要有其他解释。"""
        }]
    )
    return response.choices[0].message.content
