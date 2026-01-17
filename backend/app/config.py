"""统一配置文件 - 管理所有服务配置"""
import os
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv

# Load .env from parent folder (project root)
parent_dir = Path(__file__).resolve().parent.parent.parent
env_path = parent_dir / ".env"
load_dotenv(dotenv_path=env_path)

# ============================================
# 图片生成服务配置
# ============================================
ImageServiceType = Literal["google", "fal"]

# 默认图片生成服务：google (Google Gemini) 或 fal (FAL AI)
DEFAULT_IMAGE_SERVICE: ImageServiceType = os.getenv(
    "DEFAULT_IMAGE_SERVICE", "google"
).lower()

# Google Image Service 配置
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_DEFAULT_MODEL = os.getenv(
    "GOOGLE_DEFAULT_MODEL", "gemini-3-pro-image-preview"
)
GOOGLE_DEFAULT_ASPECT_RATIO = os.getenv("GOOGLE_DEFAULT_ASPECT_RATIO", "16:9")
GOOGLE_DEFAULT_RESOLUTION = os.getenv("GOOGLE_DEFAULT_RESOLUTION", "2K")

# Gemini 文字模型配置（用于所有文本生成）
GEMINI_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-3-flash-preview")

# FAL AI 配置
FAL_API_KEY = os.getenv("FAL_API_KEY")
FAL_DEFAULT_ENDPOINT = os.getenv("FAL_DEFAULT_ENDPOINT", "fal-ai/nano-banana")

# ============================================
# 存储服务配置
# ============================================
StorageServiceType = Literal["supabase", "local"]

# 默认存储服务：supabase 或 local
DEFAULT_STORAGE_SERVICE: StorageServiceType = os.getenv(
    "DEFAULT_STORAGE_SERVICE", "supabase"
).lower()

# Supabase 配置 (使用新的 secret key 格式: sb_secret_...)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

# 向后兼容：如果没有设置新的 SECRET_KEY，尝试使用旧的 SERVICE_KEY
if not SUPABASE_SECRET_KEY:
    SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# 本地存储配置
BASE_DIR = os.getenv("BASE_DIR", "generated_files")
USER_ID = os.getenv("USER_ID", "550e8400-e29b-41d4-a716-446655440000")

# ============================================
# 视频生成服务配置
# ============================================
# FFmpeg 路径
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")

# 视频生成默认参数
VIDEO_DEFAULT_MODEL = os.getenv("VIDEO_DEFAULT_MODEL", "wan")
VIDEO_DEFAULT_NUM_FRAMES = int(os.getenv("VIDEO_DEFAULT_NUM_FRAMES", "81"))
VIDEO_DEFAULT_FPS = int(os.getenv("VIDEO_DEFAULT_FPS", "16"))
VIDEO_DEFAULT_ASPECT_RATIO = os.getenv("VIDEO_DEFAULT_ASPECT_RATIO", "16:9")
VIDEO_DEFAULT_RESOLUTION = os.getenv("VIDEO_DEFAULT_RESOLUTION", "720p")
VIDEO_DEFAULT_INFERENCE_STEPS = int(
    os.getenv("VIDEO_DEFAULT_INFERENCE_STEPS", "30")
)

# ============================================
# API 配置
# ============================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# CORS 配置
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001"
).split(",")

# ============================================
# OpenAI 配置（用于 LLM 功能）
# ============================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_DEFAULT_MODEL = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5")


def validate_config():
    """验证必需的配置项"""
    errors = []

    if DEFAULT_IMAGE_SERVICE == "google" and not GOOGLE_API_KEY:
        errors.append("GOOGLE_API_KEY 未配置，但默认图片服务设置为 google")

    if DEFAULT_IMAGE_SERVICE == "fal" and not FAL_API_KEY:
        errors.append("FAL_API_KEY 未配置，但默认图片服务设置为 fal")

    if DEFAULT_STORAGE_SERVICE == "supabase":
        if not SUPABASE_URL:
            errors.append("SUPABASE_URL 未配置，但默认存储服务设置为 supabase")
        if not SUPABASE_SECRET_KEY:
            errors.append(
                "SUPABASE_SECRET_KEY 未配置，但默认存储服务设置为 supabase"
            )

    if errors:
        error_msg = "\n".join([f"  - {e}" for e in errors])
        print(f"⚠️  配置警告:\n{error_msg}")

    return len(errors) == 0
