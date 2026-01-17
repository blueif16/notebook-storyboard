"""视频服务 - 视频生成和拼接相关功能"""
import os
import httpx
import asyncio
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
from ..config import FFMPEG_BIN
from .storage_service import (
    ensure_folder_structure,
    save_to_supabase,
    get_image_url_from_asset_id,
    _init_supabase
)
from .image_service import fal_subscribe

# Load .env from parent folder (project root)
parent_dir = Path(__file__).resolve().parent.parent.parent.parent
env_path = parent_dir / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

async def video_gen_service(
    prompt: str,
    image_asset_id: str,
    return_id: bool = False
) -> str:
    """Generate a video from an image

    Args:
        prompt: 视频生成提示词
        image_asset_id: 参考图像的 asset_id
        return_id: 是否只返回 asset_id

    Returns:
        str: asset_id 或完整结果信息
    """
    print(f"\n{'='*60}")
    print("🎬 [VIDEO_GEN_SERVICE] 服务调用开始")
    print(f"📋 prompt={prompt}")
    print(f"📋 image_asset_id={image_asset_id}")
    print(f"📋 return_id={return_id}")
    print(f"{'='*60}\n")
    try:
        print(
            f"🔍 [VIDEO_GEN_SERVICE] 获取图片URL "
            f"(asset_id: {image_asset_id})..."
        )
        image_url = await get_image_url_from_asset_id(image_asset_id)
        if not image_url:
            raise RuntimeError("无法获取图片URL")
        print(f"✅ [VIDEO_GEN_SERVICE] 图片URL: {image_url[:80]}...")

        print("📁 [VIDEO_GEN_SERVICE] 创建文件夹结构...")
        video_folder = ensure_folder_structure("video")
        print(f"✅ [VIDEO_GEN_SERVICE] 文件夹路径: {video_folder}")

        print("🚀 [VIDEO_GEN_SERVICE] 调用FAL AI SeeDance API...")
        result = await fal_subscribe(
            "fal-ai/bytedance/seedance/v1/pro/image-to-video",
            {"prompt": prompt, "image_url": image_url}
        )
        print("✅ [VIDEO_GEN_SERVICE] FAL AI响应成功")
        print(f"📦 [VIDEO_GEN_SERVICE] 完整返回结果: {result}")

        video_url = result.get("video", {}).get("url")
        print(
            f"🔍 [VIDEO_GEN_SERVICE] 解析结果: "
            f"video对象={result.get('video')}"
        )
        if not video_url:
            raise RuntimeError("未获取到视频URL")
        print(f"🔗 [VIDEO_GEN_SERVICE] 视频URL: {video_url}")

        print("⬇️  [VIDEO_GEN_SERVICE] 下载视频...")
        async with httpx.AsyncClient(timeout=300.0) as client:
            vid_resp = await client.get(video_url)
            print(
                f"✅ [VIDEO_GEN_SERVICE] 下载完成，"
                f"大小: {len(vid_resp.content)} bytes"
            )
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.mp4"
            file_path = video_folder / filename
            with open(file_path, "wb") as f:
                f.write(vid_resp.content)
            print(f"💾 [VIDEO_GEN_SERVICE] 本地保存: {file_path}")

        print("☁️  [VIDEO_GEN_SERVICE] 上传到Supabase...")
        supabase_result = await save_to_supabase(file_path, "video")

        asset_id = None
        supabase_url = None
        supabase = _init_supabase()
        if supabase_result:
            storage_path, supabase_url = supabase_result
            if storage_path:
                print(f"✅ [VIDEO_GEN_SERVICE] Supabase路径: {storage_path}")
                if supabase:
                    try:
                        print("🔍 [VIDEO_GEN_SERVICE] 查询asset_id...")
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
                                f"✅ [VIDEO_GEN_SERVICE] "
                                f"Asset ID: {asset_id}"
                            )
                    except Exception as e:
                        print(
                            f"⚠️  [VIDEO_GEN_SERVICE] "
                            f"获取asset_id失败: {e}"
                        )

        if return_id:
            if asset_id:
                print(
                    f"🎉 [VIDEO_GEN_SERVICE] 完成! "
                    f"返回Asset ID: {asset_id}"
                )
                return asset_id
            else:
                error_msg = "Video generated but failed to get asset_id"
                print(f"⚠️  [VIDEO_GEN_SERVICE] {error_msg}")
                return error_msg
        else:
            result_msg = (
                f"Video generated successfully and saved to {file_path}. "
                f"Video URL from FAL: {video_url}"
            )
            if asset_id:
                result_msg += f" Asset ID: {asset_id}"
            if supabase_url:
                result_msg += f" Supabase URL: {supabase_url}"
            print(f"🎉 [VIDEO_GEN_SERVICE] 完成! {result_msg}")
            return result_msg
    except Exception as e:
        error = f"Video generation failed: {e}"
        print(f"❌ [VIDEO_GEN_SERVICE] 错误: {error}")
        return error

async def run_ffmpeg(cmd: List[str]):
    """执行FFmpeg命令"""
    logger.info(f"执行FFmpeg命令: {' '.join(cmd)}")
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        error_msg = stderr.decode() if stderr else "未知错误"
        logger.error(f"FFmpeg执行失败: {error_msg}")
        raise RuntimeError(f"FFmpeg执行失败: {error_msg}")
    return stdout.decode() if stdout else ""

def ensure_output_dir(output_path: Path) -> Path:
    """确保输出目录存在"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path

async def stitch_videos(segment_paths: List[str], output_path: str, trim_duration: float = 7.9) -> str:
    """拼接多个视频片段为一个完整视频"""
    if not segment_paths:
        raise ValueError("视频片段列表不能为空")

    output = ensure_output_dir(Path(output_path))
    logger.info(f"开始拼接 {len(segment_paths)} 个视频片段到: {output}")

    if len(segment_paths) == 1:
        cmd = [FFMPEG_BIN, "-i", segment_paths[0], "-c", "copy", "-y", str(output)]
        await run_ffmpeg(cmd)
        logger.info(f"单个片段直接复制完成: {output}")
        return str(output)

    filter_complex = []
    concat_inputs = []

    for i, path in enumerate(segment_paths):
        is_last = (i == len(segment_paths) - 1)
        if is_last:
            concat_inputs.append(f"[{i}:v]")
        else:
            filter_complex.append(f"[{i}:v]trim=duration={trim_duration},setpts=PTS-STARTPTS[v{i}]")
            concat_inputs.append(f"[v{i}]")

    if filter_complex:
        concat_filter = ";".join(filter_complex) + ";" + "".join(concat_inputs) + f"concat=n={len(segment_paths)}:v=1:a=0[out]"
    else:
        concat_filter = "".join(concat_inputs) + f"concat=n={len(segment_paths)}:v=1:a=0[out]"

    cmd = [FFMPEG_BIN]
    for path in segment_paths:
        cmd.extend(["-i", path])
    cmd.extend([
        "-filter_complex", concat_filter,
        "-map", "[out]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-y", str(output)
    ])

    await run_ffmpeg(cmd)
    logger.info(f"视频拼接完成: {output}")
    return str(output)


async def first_end_to_video(
    prompt: str,
    first_frame_asset_id: str,
    last_frame_asset_id: str,
    model: str = "wan",
    num_frames: int = 81,
    frames_per_second: int = 16,
    aspect_ratio: str = "auto",
    resolution: str = "720p",
    num_inference_steps: int = 30,
    return_id: bool = False,
    return_path: bool = False
) -> str:
    """Generate video from first and last frame

    Args:
        prompt: 视频生成提示词
        first_frame_asset_id: 第一帧图像的 asset_id
        last_frame_asset_id: 最后一帧图像的 asset_id
        model: 使用的模型，"wan" 或 "veo"
        num_frames: 帧数
        frames_per_second: 帧率
        aspect_ratio: 宽高比
        resolution: 分辨率
        num_inference_steps: 推理步数
        return_id: 是否只返回 asset_id
        return_path: 是否返回本地路径

    Returns:
        str: asset_id、本地路径或完整结果信息
    """
    print(f"\n{'='*60}")
    print("🎬 [FIRST_END_TO_VIDEO] 服务调用开始")
    print(f"📋 model={model}")
    print(f"📋 prompt={prompt}")
    print(f"📋 first_frame_asset_id={first_frame_asset_id}")
    print(f"📋 last_frame_asset_id={last_frame_asset_id}")
    print(
        f"📋 num_frames={num_frames}, "
        f"frames_per_second={frames_per_second}"
    )
    print(f"📋 aspect_ratio={aspect_ratio}, resolution={resolution}")
    print(f"📋 num_inference_steps={num_inference_steps}")
    print(f"📋 return_id={return_id}, return_path={return_path}")
    print(f"{'='*60}\n")
    try:
        print(
            f"🔍 [FIRST_END_TO_VIDEO] 获取第一帧URL "
            f"(asset_id: {first_frame_asset_id})..."
        )
        first_frame_url = await get_image_url_from_asset_id(
            first_frame_asset_id
        )
        if not first_frame_url:
            raise RuntimeError("无法获取第一帧图片URL")
        print(f"✅ [FIRST_END_TO_VIDEO] 第一帧URL: {first_frame_url[:80]}...")

        print(
            f"🔍 [FIRST_END_TO_VIDEO] 获取最后一帧URL "
            f"(asset_id: {last_frame_asset_id})..."
        )
        last_frame_url = await get_image_url_from_asset_id(last_frame_asset_id)
        if not last_frame_url:
            raise RuntimeError("无法获取最后一帧图片URL")
        print(
            f"✅ [FIRST_END_TO_VIDEO] "
            f"最后一帧URL: {last_frame_url[:80]}..."
        )

        print("📁 [FIRST_END_TO_VIDEO] 创建文件夹结构...")
        video_folder = ensure_folder_structure("video")
        print(f"✅ [FIRST_END_TO_VIDEO] 文件夹路径: {video_folder}")

        if model == "wan":
            api_params = {
                "start_image_url": first_frame_url,
                "end_image_url": last_frame_url,
                "prompt": prompt,
                "num_frames": num_frames,
                "frames_per_second": frames_per_second,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "num_inference_steps": num_inference_steps
            }
            endpoint = "fal-ai/wan-flf2v"
            print("🚀 [FIRST_END_TO_VIDEO] 调用FAL AI Wan-2.1 API...")
        elif model == "veo":
            duration = f"{int(num_frames/frames_per_second)}s"
            api_params = {
                "first_frame_url": first_frame_url,
                "last_frame_url": last_frame_url,
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "generate_audio": False
            }
            endpoint = "fal-ai/veo3.1/fast/first-last-frame-to-video"
            print("🚀 [FIRST_END_TO_VIDEO] 调用FAL AI Veo3.1 API...")
        else:
            raise ValueError(
                f"不支持的模型: {model}. 支持的模型: wan, veo"
            )

        print(f"📋 [FIRST_END_TO_VIDEO] API参数: {api_params}")
        result = await fal_subscribe(endpoint, api_params)
        print("✅ [FIRST_END_TO_VIDEO] FAL AI响应成功")
        print(f"📦 [FIRST_END_TO_VIDEO] 完整返回结果: {result}")

        video_url = result.get("video", {}).get("url")
        print(
            f"🔍 [FIRST_END_TO_VIDEO] 解析结果: "
            f"video对象={result.get('video')}"
        )
        if not video_url:
            raise RuntimeError("未获取到视频URL")
        print(f"🔗 [FIRST_END_TO_VIDEO] 视频URL: {video_url}")

        print("⬇️  [FIRST_END_TO_VIDEO] 下载视频...")
        async with httpx.AsyncClient(timeout=300.0) as client:
            vid_resp = await client.get(video_url)
            print(
                f"✅ [FIRST_END_TO_VIDEO] 下载完成，"
                f"大小: {len(vid_resp.content)} bytes"
            )
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_flf2v_{timestamp}.mp4"
            file_path = video_folder / filename
            with open(file_path, "wb") as f:
                f.write(vid_resp.content)
            print(f"💾 [FIRST_END_TO_VIDEO] 本地保存: {file_path}")

        print("☁️  [FIRST_END_TO_VIDEO] 上传到Supabase...")
        supabase_result = await save_to_supabase(file_path, "video")

        asset_id = None
        supabase_url = None
        supabase = _init_supabase()
        if supabase_result:
            storage_path, supabase_url = supabase_result
            if storage_path:
                print(f"✅ [FIRST_END_TO_VIDEO] Supabase路径: {storage_path}")
                if supabase:
                    try:
                        print("🔍 [FIRST_END_TO_VIDEO] 查询asset_id...")
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
                                f"✅ [FIRST_END_TO_VIDEO] "
                                f"Asset ID: {asset_id}"
                            )
                    except Exception as e:
                        print(
                            f"⚠️  [FIRST_END_TO_VIDEO] "
                            f"获取asset_id失败: {e}"
                        )

        if return_id:
            if asset_id:
                print(
                    f"🎉 [FIRST_END_TO_VIDEO] 完成! "
                    f"返回Asset ID: {asset_id}"
                )
                return asset_id
            else:
                error_msg = (
                    "Video generated from first-last frames "
                    "but failed to get asset_id"
                )
                print(f"⚠️  [FIRST_END_TO_VIDEO] {error_msg}")
                return error_msg
        elif return_path:
            print(
                f"🎉 [FIRST_END_TO_VIDEO] 完成! "
                f"返回本地路径: {file_path}"
            )
            return str(file_path)
        else:
            result_msg = (
                f"Video generated successfully from first-last frames "
                f"and saved to {file_path}. "
                f"Video URL from FAL: {video_url}"
            )
            if asset_id:
                result_msg += f" Asset ID: {asset_id}"
            if supabase_url:
                result_msg += f" Supabase URL: {supabase_url}"
            print(f"🎉 [FIRST_END_TO_VIDEO] 完成! {result_msg}")
            return result_msg
    except Exception as e:
        error = f"First-last frame to video generation failed: {e}"
        print(f"❌ [FIRST_END_TO_VIDEO] 错误: {error}")
        return error
