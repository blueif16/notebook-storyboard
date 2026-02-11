"""图像生成服务 - 统一图像生成接口，支持多种服务"""
import os
import httpx
import asyncio
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
from ..config import (
    DEFAULT_IMAGE_SERVICE,
    FAL_API_KEY,
    FAL_DEFAULT_ENDPOINT,
    GOOGLE_API_KEY,
    GOOGLE_DEFAULT_MODEL
)
from .storage_service import (
    ensure_folder_structure,
    save_to_supabase,
    get_image_url_from_asset_id,
    _init_supabase
)

# Load .env from parent folder (project root)
parent_dir = Path(__file__).resolve().parent.parent.parent.parent
env_path = parent_dir / ".env"
load_dotenv(dotenv_path=env_path)

async def fal_subscribe(endpoint: str, args: dict) -> dict:
    """订阅FAL任务并等待结果"""
    if not FAL_API_KEY or FAL_API_KEY.strip() == "":
        raise ValueError("❌ FAL_API_KEY未设置或为空，请在.env文件中配置FAL_API_KEY")
    base_url = "https://queue.fal.run"
    headers = {"Authorization": f"Key {FAL_API_KEY}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"📤 [FAL_API] Endpoint: {endpoint}")
        print(f"📤 [FAL_API] 请求参数: {args}")
        resp = await client.post(f"{base_url}/{endpoint}", headers=headers, json=args)
        print(f"📤 [FAL_API] 提交状态码: {resp.status_code}")
        if resp.status_code != 200:
            print(f"❌ [FAL_API] 提交失败响应: {resp.text[:500]}")
            raise RuntimeError(f"FAL提交失败: {resp.status_code}, {resp.text[:200]}")
        result = resp.json()
        request_id = result.get("request_id")
        status_url = result.get("status_url")
        response_url = result.get("response_url")
        print(f"✅ [FAL_API] 请求已提交: {request_id}")
        print(f"📋 [FAL_API] status_url: {status_url}")
        print(f"📋 [FAL_API] response_url: {response_url}")

        if not status_url:
            print(f"⚠️  [FAL_API] 响应中无status_url，使用构建的URL")
            status_url = f"{base_url}/{endpoint}/requests/{request_id}/status"

        poll_count = 0
        for _ in range(150):
            poll_count += 1
            await asyncio.sleep(2)
            poll_url = f"{status_url}?logs=1" if "?" not in status_url else f"{status_url}&logs=1"
            print(f"🔄 [FAL_API] 第{poll_count}次轮询: {poll_url}")
            status_resp = await client.get(poll_url, headers=headers)
            if status_resp.status_code not in [200, 202]:
                print(f"⚠️  [FAL_API] 第{poll_count}次状态查询失败: HTTP {status_resp.status_code}")
                print(f"⚠️  [FAL_API] 响应内容: {status_resp.text[:300]}")
                print(f"⚠️  [FAL_API] 请求URL: {poll_url}")
                continue
            status_data = status_resp.json()
            status_value = status_data.get("status")
            print(f"📊 [FAL_API] 第{poll_count}次状态: {status_value}")
            if status_value == "COMPLETED":
                print(f"✅ [FAL_API] 任务完成")
                return status_data
            elif status_value in ["FAILED", "CANCELLED"]:
                error_msg = status_data.get("error", "Unknown error")
                print(f"❌ [FAL_API] 任务失败: {error_msg}")
                raise RuntimeError(f"FAL任务失败: {error_msg}")
        raise RuntimeError("FAL任务超时")

async def image_gen_service(
    prompt: str,
    return_id: bool = False
) -> str:
    """Generate an image from text prompt

    Args:
        prompt: 图像生成提示词
        return_id: 是否只返回 asset_id

    Returns:
        str: asset_id 或完整结果信息
    """
    print(f"\n{'='*60}")
    print("🎨 [IMAGE_GEN_SERVICE] 服务调用开始")
    print(f"📋 prompt={prompt}")
    print(f"📋 return_id={return_id}")
    print(f"{'='*60}\n")
    try:
        print("📁 [IMAGE_GEN_SERVICE] 创建文件夹结构...")
        image_folder = ensure_folder_structure("image")
        print(f"✅ [IMAGE_GEN_SERVICE] 文件夹路径: {image_folder}")

        print("🚀 [IMAGE_GEN_SERVICE] 调用FAL AI API...")
        result = await fal_subscribe(
            "fal-ai/nano-banana",
            {
                "prompt": prompt,
                "num_images": 1,
                "aspect_ratio": "1:1",
                "output_format": "jpeg"
            }
        )
        print("✅ [IMAGE_GEN_SERVICE] FAL AI响应成功")
        print(f"📦 [IMAGE_GEN_SERVICE] 完整返回结果: {result}")

        image_url = result.get("images", [{}])[0].get("url")
        print(
            f"🔍 [IMAGE_GEN_SERVICE] 解析结果: "
            f"images数组={result.get('images')}"
        )
        if not image_url:
            raise RuntimeError("未获取到图片URL")
        print(f"🔗 [IMAGE_GEN_SERVICE] 图片URL: {image_url}")

        print("⬇️  [IMAGE_GEN_SERVICE] 下载图片...")
        async with httpx.AsyncClient() as client:
            img_resp = await client.get(image_url)
            print(
                f"✅ [IMAGE_GEN_SERVICE] 下载完成，"
                f"大小: {len(img_resp.content)} bytes"
            )
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.jpg"
            file_path = image_folder / filename
            with open(file_path, "wb") as f:
                f.write(img_resp.content)
            print(f"💾 [IMAGE_GEN_SERVICE] 本地保存: {file_path}")

        print("☁️  [IMAGE_GEN_SERVICE] 上传到Supabase...")
        supabase_result = await save_to_supabase(file_path, "image")

        asset_id = None
        supabase_url = None
        supabase = _init_supabase()
        if supabase_result:
            storage_path, supabase_url = supabase_result
            if storage_path and supabase:
                try:
                    print("🔍 [IMAGE_GEN_SERVICE] 查询asset_id...")
                    db_resp = (
                        supabase.table("user_images")
                        .select("id")
                        .eq("storage_path", storage_path)
                        .single()
                        .execute()
                    )
                    if db_resp.data:
                        asset_id = db_resp.data.get("id")
                        print(f"✅ [IMAGE_GEN_SERVICE] Asset ID: {asset_id}")
                except Exception as e:
                    print(f"⚠️  [IMAGE_GEN_SERVICE] 获取asset_id失败: {e}")

        if return_id:
            if asset_id:
                print(
                    f"🎉 [IMAGE_GEN_SERVICE] 完成! "
                    f"返回Asset ID: {asset_id}"
                )
                return asset_id
            else:
                error_msg = "Image generated but failed to get asset_id"
                print(f"⚠️  [IMAGE_GEN_SERVICE] {error_msg}")
                return error_msg
        else:
            result_msg = (
                f"Image generated successfully and saved to {file_path}. "
                f"Image URL from FAL: {image_url}"
            )
            if asset_id:
                result_msg += f" Asset ID: {asset_id}"
            if supabase_url:
                result_msg += f" Supabase URL: {supabase_url}"
            print(f"🎉 [IMAGE_GEN_SERVICE] 完成! {result_msg}")
            return result_msg
    except Exception as e:
        error = f"Image generation failed: {e}"
        print(f"❌ [IMAGE_GEN_SERVICE] 错误: {error}")
        return error


async def image_to_image_gen_service(
    prompt: str,
    image_asset_id,
    aspect_ratio: str = "16:9",
    return_id: bool = False
) -> str:
    """Generate an image from reference image(s)

    Args:
        prompt: 图像生成提示词
        image_asset_id: 参考图像的 asset_id，可以是单个字符串或字符串列表
        aspect_ratio: 图像宽高比，默认 "9:16"
        return_id: 是否只返回 asset_id

    Returns:
        str: asset_id 或完整结果信息
    """
    print(f"\n{'='*60}")
    print("🎨 [IMAGE_TO_IMAGE_SERVICE] 服务调用开始")
    print(f"📋 prompt长度: {len(prompt)} 字符")
    print(f"📋 image_asset_id={image_asset_id}")
    print(f"📋 image_asset_id类型: {type(image_asset_id)}")
    print(f"📋 aspect_ratio={aspect_ratio}")
    print(f"📋 return_id={return_id}")
    print(f"{'='*60}\n")
    try:
        if isinstance(image_asset_id, str):
            asset_ids = [image_asset_id]
            print("🔍 [IMAGE_TO_IMAGE_SERVICE] 单个图片模式")
        elif isinstance(image_asset_id, list):
            asset_ids = image_asset_id
            print(
                f"🔍 [IMAGE_TO_IMAGE_SERVICE] 多图片模式，"
                f"共{len(asset_ids)}张"
            )
        else:
            raise RuntimeError(
                f"不支持的image_asset_id类型: {type(image_asset_id)}"
            )

        ref_image_urls = []
        for idx, asset_id in enumerate(asset_ids):
            print(
                f"🔍 [IMAGE_TO_IMAGE_SERVICE] 获取第{idx+1}张参考图片URL "
                f"(asset_id: {asset_id})..."
            )
            ref_url = await get_image_url_from_asset_id(asset_id)
            if not ref_url:
                print(
                    f"⚠️  [IMAGE_TO_IMAGE_SERVICE] "
                    f"无法获取asset_id={asset_id}的URL，跳过"
                )
                continue
            ref_image_urls.append(ref_url)
            print(
                f"✅ [IMAGE_TO_IMAGE_SERVICE] "
                f"第{idx+1}张URL长度: {len(ref_url)}"
            )
            print(
                f"🔗 [IMAGE_TO_IMAGE_SERVICE] "
                f"URL前缀: {ref_url[:80]}..."
            )

        if not ref_image_urls:
            raise RuntimeError("未能获取任何参考图片URL")

        print("📁 [IMAGE_TO_IMAGE_SERVICE] 创建文件夹结构...")
        image_folder = ensure_folder_structure("image")
        print(f"✅ [IMAGE_TO_IMAGE_SERVICE] 文件夹路径: {image_folder}")

        print("🚀 [IMAGE_TO_IMAGE_SERVICE] 调用FAL AI API...")
        fal_args = {
            "prompt": prompt,
            "image_url": (
                ref_image_urls[0] if len(ref_image_urls) == 1
                else ref_image_urls
            ),
            "num_images": 1,
            "aspect_ratio": aspect_ratio,
            "output_format": "jpeg"
        }
        print(f"📋 [IMAGE_TO_IMAGE_SERVICE] FAL参数: {fal_args}")
        result = await fal_subscribe("fal-ai/nano-banana", fal_args)
        print("✅ [IMAGE_TO_IMAGE_SERVICE] FAL AI响应成功")

        image_url = result.get("images", [{}])[0].get("url")
        if not image_url:
            raise RuntimeError("未获取到图片URL")
        print(f"🔗 [IMAGE_TO_IMAGE_SERVICE] 图片URL: {image_url}")

        print("⬇️  [IMAGE_TO_IMAGE_SERVICE] 下载图片...")
        async with httpx.AsyncClient() as client:
            img_resp = await client.get(image_url)
            print(
                f"✅ [IMAGE_TO_IMAGE_SERVICE] 下载完成，"
                f"大小: {len(img_resp.content)} bytes"
            )
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.jpg"
            file_path = image_folder / filename
            with open(file_path, "wb") as f:
                f.write(img_resp.content)
            print(f"💾 [IMAGE_TO_IMAGE_SERVICE] 本地保存: {file_path}")

        print("☁️  [IMAGE_TO_IMAGE_SERVICE] 上传到Supabase...")
        supabase_result = await save_to_supabase(file_path, "image")

        asset_id = None
        supabase_url = None
        supabase = _init_supabase()
        if supabase_result:
            storage_path, supabase_url = supabase_result
            if storage_path and supabase:
                try:
                    print("🔍 [IMAGE_TO_IMAGE_SERVICE] 查询asset_id...")
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
                            f"✅ [IMAGE_TO_IMAGE_SERVICE] "
                            f"Asset ID: {asset_id}"
                        )
                except Exception as e:
                    print(
                        f"⚠️  [IMAGE_TO_IMAGE_SERVICE] "
                        f"获取asset_id失败: {e}"
                    )

        if return_id:
            if asset_id:
                print(
                    f"🎉 [IMAGE_TO_IMAGE_SERVICE] 完成! "
                    f"返回Asset ID: {asset_id}"
                )
                return asset_id
            else:
                error_msg = "Image generated but failed to get asset_id"
                print(f"⚠️  [IMAGE_TO_IMAGE_SERVICE] {error_msg}")
                return error_msg
        else:
            result_msg = (
                f"Image generated successfully and saved to {file_path}. "
                f"Image URL from FAL: {image_url}"
            )
            if asset_id:
                result_msg += f" Asset ID: {asset_id}"
            if supabase_url:
                result_msg += f" Supabase URL: {supabase_url}"
            print(f"🎉 [IMAGE_TO_IMAGE_SERVICE] 完成! {result_msg}")
            return result_msg
    except Exception as e:
        error = f"Image to image generation failed: {e}"
        print(f"❌ [IMAGE_TO_IMAGE_SERVICE] 错误: {error}")
        return error


# ============================================
# 统一图像生成接口（根据配置自动选择服务）
# ============================================

async def unified_image_gen_service(
    prompt: str,
    return_id: bool = False,
    service: Optional[str] = None
) -> str:
    """统一图像生成接口 - 根据配置自动选择服务

    Args:
        prompt: 图像生成提示词
        return_id: 是否只返回 asset_id
        service: 指定服务类型 ("google" 或 "fal")，None 则使用默认配置

    Returns:
        str: asset_id 或完整结果信息
    """
    from .google_image_service import google_text_to_image

    selected_service = service or DEFAULT_IMAGE_SERVICE

    if selected_service == "google":
        return await google_text_to_image(
            prompt=prompt,
            model=GOOGLE_DEFAULT_MODEL,
            return_id=return_id
        )
    elif selected_service == "fal":
        return await image_gen_service(
            prompt=prompt,
            return_id=return_id
        )
    else:
        raise ValueError(
            f"不支持的图像服务: {selected_service}. "
            f"支持的服务: google, fal"
        )


async def unified_image_to_image_gen_service(
    prompt: str,
    image_asset_id,
    aspect_ratio: str = "9:16",
    return_id: bool = False,
    service: Optional[str] = None
) -> str:
    """统一图像编辑接口 - 根据配置自动选择服务

    Args:
        prompt: 图像生成提示词
        image_asset_id: 参考图像的 asset_id，可以是单个字符串或字符串列表
        aspect_ratio: 图像宽高比，默认 "9:16"
        return_id: 是否只返回 asset_id
        service: 指定服务类型 ("google" 或 "fal")，None 则使用默认配置

    Returns:
        str: asset_id 或完整结果信息
    """
    from .google_image_service import google_image_to_image

    selected_service = service or DEFAULT_IMAGE_SERVICE

    if selected_service == "google":
        # Google 服务目前只支持单张图片
        if isinstance(image_asset_id, list):
            image_asset_id = image_asset_id[0]
        return await google_image_to_image(
            prompt=prompt,
            image_asset_id=image_asset_id,
            model=GOOGLE_DEFAULT_MODEL,
            return_id=return_id
        )
    elif selected_service == "fal":
        return await image_to_image_gen_service(
            prompt=prompt,
            image_asset_id=image_asset_id,
            aspect_ratio=aspect_ratio,
            return_id=return_id
        )
    else:
        raise ValueError(
            f"不支持的图像服务: {selected_service}. "
            f"支持的服务: google, fal"
        )
