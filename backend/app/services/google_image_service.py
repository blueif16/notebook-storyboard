"""Google Gemini图像生成服务"""
import httpx
from pathlib import Path
from typing import Optional, List, Union, Any
from datetime import datetime
from ..config import (
    GOOGLE_API_KEY,
    GOOGLE_DEFAULT_MODEL,
    GOOGLE_DEFAULT_ASPECT_RATIO,
    GOOGLE_DEFAULT_RESOLUTION
)
from .storage_service import (
    save_image_to_supabase,
    _init_supabase
)


class GoogleImageService:
    """Google Gemini图像生成服务类"""

    def __init__(self):
        self.api_key = GOOGLE_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.default_model = GOOGLE_DEFAULT_MODEL

    async def _call_gemini_api(
        self,
        model: str,
        prompt: str,
        image_urls: Optional[List[str]] = None,
        aspect_ratio: Optional[str] = None,
        resolution: Optional[str] = None
    ) -> dict:
        """调用Gemini API生成图像"""
        url = (
            f"{self.base_url}/models/{model}:generateContent"
            f"?key={self.api_key}"
        )

        # 构建请求内容 - parts 数组
        parts = [{"text": prompt}]

        # 添加参考图像
        if image_urls:
            for img_url in image_urls:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    img_resp = await client.get(img_url)
                    import base64
                    img_b64 = base64.b64encode(img_resp.content).decode()
                    parts.append({
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": img_b64
                        }
                    })

        # 构建 payload
        payload: dict[str, Any] = {
            "contents": [{"parts": parts}]
        }

        # 添加生成配置
        generation_config: dict[str, Any] = {
            "responseModalities": ["TEXT", "IMAGE"]
        }

        # 添加图像配置
        # Note: imageSize is only supported by gemini-3-* models
        supports_image_size = "gemini-3" in model
        if aspect_ratio or (resolution and supports_image_size):
            image_config: dict[str, str] = {}
            if aspect_ratio:
                image_config["aspectRatio"] = aspect_ratio
            if resolution and supports_image_size:
                image_config["imageSize"] = resolution
            if image_config:  # Only add if we have at least one property
                generation_config["imageConfig"] = image_config

        payload["generationConfig"] = generation_config

        print(f"📤 [GOOGLE_IMAGE_API] 调用模型: {model}")
        print(f"📤 [GOOGLE_IMAGE_API] Prompt长度: {len(prompt)}")
        if image_urls:
            print(f"📤 [GOOGLE_IMAGE_API] 参考图片数量: {len(image_urls)}")

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload)
            print(f"📤 [GOOGLE_IMAGE_API] 响应状态: {resp.status_code}")

            if resp.status_code != 200:
                print(
                    f"❌ [GOOGLE_IMAGE_API] 错误响应: {resp.text[:500]}"
                )
                raise RuntimeError(
                    f"Gemini API调用失败: {resp.status_code}, "
                    f"{resp.text[:200]}"
                )

            return resp.json()

    async def _extract_image_from_response(
        self, response: dict
    ) -> Optional[bytes]:
        """从响应中提取图像数据"""
        try:
            print(f"🔍 [DEBUG] 响应结构: {list(response.keys())}")
            candidates = response.get("candidates", [])
            if not candidates:
                print("⚠️  [GOOGLE_IMAGE_API] 响应中无candidates")
                print(f"🔍 [DEBUG] 完整响应: {response}")
                return None

            print(f"🔍 [DEBUG] Candidates数量: {len(candidates)}")
            parts = candidates[0].get("content", {}).get("parts", [])
            print(f"🔍 [DEBUG] Parts数量: {len(parts)}")

            for i, part in enumerate(parts):
                print(f"🔍 [DEBUG] Part {i} keys: {list(part.keys())}")
                # Try both camelCase and snake_case
                inline_data = part.get("inline_data") or part.get("inlineData")
                if inline_data:
                    import base64
                    img_data = inline_data.get("data")
                    if img_data:
                        print(f"✅ [DEBUG] 找到图像数据，长度: {len(img_data)}")
                        return base64.b64decode(img_data)

            print("⚠️  [GOOGLE_IMAGE_API] 未找到图像数据")
            return None
        except Exception as e:
            print(f"❌ [GOOGLE_IMAGE_API] 提取图像失败: {e}")
            import traceback
            traceback.print_exc()
            return None


async def google_text_to_image(
    prompt: str,
    model: str = "gemini-2.5-flash-image",
    return_id: bool = False,
    local_save_path: Optional[str] = None
) -> str:
    """文本生成图像

    Args:
        prompt: 图像生成提示词
        model: 使用的模型，默认 "gemini-2.5-flash-image"
        return_id: 是否只返回 asset_id
        local_save_path: 可选的本地保存路径（如果提供，会额外保存到该路径）

    Returns:
        str: asset_id 或完整结果信息
    """
    print(f"\n{'='*60}")
    print("🎨 [GOOGLE_TEXT_TO_IMAGE] 服务调用开始")
    print(f"📋 prompt={prompt}")
    print(f"📋 model={model}")
    print(f"{'='*60}\n")

    try:
        service = GoogleImageService()

        print("🚀 [GOOGLE_TEXT_TO_IMAGE] 调用Google Gemini API...")
        response = await service._call_gemini_api(model, prompt)

        print("📦 [GOOGLE_TEXT_TO_IMAGE] 提取图像数据...")
        image_data = await service._extract_image_from_response(response)

        if not image_data:
            raise RuntimeError("未能从响应中提取图像数据")

        # 如果提供了本地保存路径，先保存到本地
        if local_save_path:
            print(f"💾 [GOOGLE_TEXT_TO_IMAGE] 保存到本地: {local_save_path}")
            local_path = Path(local_save_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(image_data)
            print(f"✅ [GOOGLE_TEXT_TO_IMAGE] 本地保存成功")

        print("💾 [GOOGLE_TEXT_TO_IMAGE] 保存图像...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"google_image_{timestamp}.jpg"

        print("☁️  [GOOGLE_TEXT_TO_IMAGE] 上传到Supabase...")
        supabase_result = await save_image_to_supabase(
            image_data, filename
        )

        asset_id = None
        supabase_url = None
        supabase = _init_supabase()
        if supabase_result:
            storage_path, supabase_url = supabase_result
            if storage_path and supabase:
                try:
                    print("🔍 [GOOGLE_TEXT_TO_IMAGE] 查询asset_id...")
                    db_resp = (
                        supabase.table("user_images")
                        .select("id")
                        .eq("storage_path", storage_path)
                        .single()
                        .execute()
                    )
                    if db_resp.data:
                        asset_id = db_resp.data.get("id")
                        print(f"✅ [GOOGLE_TEXT_TO_IMAGE] Asset ID: {asset_id}")
                except Exception as e:
                    print(
                        f"⚠️  [GOOGLE_TEXT_TO_IMAGE] 获取asset_id失败: {e}"
                    )

        if return_id:
            if asset_id:
                print(
                    f"🎉 [GOOGLE_TEXT_TO_IMAGE] 完成! "
                    f"返回Asset ID: {asset_id}"
                )
                return asset_id
            else:
                error_msg = "Image generated but failed to get asset_id"
                print(f"⚠️  [GOOGLE_TEXT_TO_IMAGE] {error_msg}")
                return error_msg
        else:
            result_msg = "Image generated successfully."
            if asset_id:
                result_msg += f" Asset ID: {asset_id}"
            if supabase_url:
                result_msg += f" Supabase URL: {supabase_url}"
            print(f"🎉 [GOOGLE_TEXT_TO_IMAGE] 完成! {result_msg}")
            return result_msg

    except Exception as e:
        error = f"Google text-to-image generation failed: {e}"
        print(f"❌ [GOOGLE_TEXT_TO_IMAGE] 错误: {error}")
        raise RuntimeError(error) from e


async def google_image_to_image(
    prompt: str,
    image_asset_ids: Union[str, List[str]],
    model: str = "gemini-2.5-flash-image",
    aspect_ratio: Optional[str] = None,
    resolution: Optional[str] = None,
    return_id: bool = False,
    local_save_path: Optional[str] = None
) -> str:
    """图像编辑（基于参考图像生成新图像）

    Args:
        prompt: 图像编辑提示词
        image_asset_ids: 参考图像的 asset_id（单个或列表，最多14张）
        model: 使用的模型，默认 "gemini-2.5-flash-image"
        aspect_ratio: 图像宽高比，如 "16:9", "1:1" 等，默认使用配置文件设置
        resolution: 图像分辨率，如 "1K", "2K", "4K"，默认使用配置文件设置
        return_id: 是否只返回 asset_id
        local_save_path: 可选的本地保存路径（如果提供，会额外保存到该路径）

    Returns:
        str: asset_id 或完整结果信息
    """
    print(f"\n{'='*60}")
    print("🎨 [GOOGLE_IMAGE_TO_IMAGE] 服务调用开始")
    print(f"📋 prompt长度: {len(prompt)} 字符")
    print(f"📋 image_asset_ids={image_asset_ids}")
    print(f"📋 model={model}")
    print(f"{'='*60}\n")

    try:
        from .storage_service import get_image_url_from_asset_id

        service = GoogleImageService()

        # 处理单个或多个 asset_id
        asset_id_list = [image_asset_ids] if isinstance(image_asset_ids, str) else image_asset_ids

        if len(asset_id_list) > 14:
            raise ValueError(f"最多支持14张参考图片，当前提供了{len(asset_id_list)}张")

        print(f"🔍 [GOOGLE_IMAGE_TO_IMAGE] 获取{len(asset_id_list)}张参考图片URL...")
        ref_image_urls = []
        for asset_id in asset_id_list:
            print(f"  - 获取 asset_id: {asset_id}")
            url = await get_image_url_from_asset_id(asset_id)
            if not url:
                raise RuntimeError(f"无法获取asset_id={asset_id}的URL")
            ref_image_urls.append(url)
            print(f"  - URL长度: {len(url)}")
        print(f"✅ [GOOGLE_IMAGE_TO_IMAGE] {len(ref_image_urls)}张参考图片URL获取成功")

        print("🚀 [GOOGLE_IMAGE_TO_IMAGE] 调用Google Gemini API...")
        print(f"  - Prompt: {prompt[:100]}...")
        print(f"  - Aspect ratio: {aspect_ratio or GOOGLE_DEFAULT_ASPECT_RATIO}")
        print(f"  - Resolution: {resolution or GOOGLE_DEFAULT_RESOLUTION}")
        response = await service._call_gemini_api(
            model, prompt, image_urls=ref_image_urls,
            aspect_ratio=aspect_ratio or GOOGLE_DEFAULT_ASPECT_RATIO,
            resolution=resolution or GOOGLE_DEFAULT_RESOLUTION
        )

        print("📦 [GOOGLE_IMAGE_TO_IMAGE] 提取图像数据...")
        image_data = await service._extract_image_from_response(response)

        if not image_data:
            raise RuntimeError("未能从响应中提取图像数据")

        # 如果提供了本地保存路径，先保存到本地
        if local_save_path:
            print(f"💾 [GOOGLE_IMAGE_TO_IMAGE] 保存到本地: {local_save_path}")
            local_path = Path(local_save_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(image_data)
            print(f"✅ [GOOGLE_IMAGE_TO_IMAGE] 本地保存成功")

        print("💾 [GOOGLE_IMAGE_TO_IMAGE] 保存图像...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"google_edited_{timestamp}.jpg"

        print("☁️  [GOOGLE_IMAGE_TO_IMAGE] 上传到Supabase...")
        supabase_result = await save_image_to_supabase(
            image_data, filename
        )

        asset_id = None
        supabase_url = None
        supabase = _init_supabase()
        if supabase_result:
            storage_path, supabase_url = supabase_result
            if storage_path and supabase:
                try:
                    print("🔍 [GOOGLE_IMAGE_TO_IMAGE] 查询asset_id...")
                    db_resp = (
                        supabase.table("user_images")
                        .select("id")
                        .eq("storage_path", storage_path)
                        .single()
                        .execute()
                    )
                    if db_resp.data:
                        asset_id = db_resp.data.get("id")
                        print(
                            f"✅ [GOOGLE_IMAGE_TO_IMAGE] "
                            f"Asset ID: {asset_id}"
                        )
                except Exception as e:
                    print(
                        f"⚠️  [GOOGLE_IMAGE_TO_IMAGE] "
                        f"获取asset_id失败: {e}"
                    )

        if return_id:
            if asset_id:
                print(
                    f"🎉 [GOOGLE_IMAGE_TO_IMAGE] 完成! "
                    f"返回Asset ID: {asset_id}"
                )
                return asset_id
            else:
                error_msg = "Image generated but failed to get asset_id"
                print(f"⚠️  [GOOGLE_IMAGE_TO_IMAGE] {error_msg}")
                return error_msg
        else:
            result_msg = "Image edited successfully."
            if asset_id:
                result_msg += f" Asset ID: {asset_id}"
            if supabase_url:
                result_msg += f" Supabase URL: {supabase_url}"
            print(f"🎉 [GOOGLE_IMAGE_TO_IMAGE] 完成! {result_msg}")
            return result_msg

    except Exception as e:
        error = f"Google image-to-image generation failed: {e}"
        print(f"❌ [GOOGLE_IMAGE_TO_IMAGE] 错误: {error}")
        raise RuntimeError(error) from e
