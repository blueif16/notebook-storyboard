"""存储服务 - Supabase核心功能"""
from pathlib import Path
from typing import Optional, Any, Tuple
from contextvars import ContextVar
from ..config import SUPABASE_URL, SUPABASE_SECRET_KEY, USER_ID, BASE_DIR

current_user_id: ContextVar[Optional[str]] = ContextVar(
    'current_user_id', default=None
)
supabase: Optional[Any] = None
_supabase_initialized = False


def _init_supabase():
    global supabase, _supabase_initialized
    if _supabase_initialized:
        return supabase
    try:
        from supabase import create_client
        if SUPABASE_URL and SUPABASE_SECRET_KEY:
            supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
        _supabase_initialized = True
    except ImportError:
        print("⚠️ Supabase not available")
    except Exception as e:
        print(f"⚠️ Supabase initialization failed: {e}")
    return supabase


async def save_image_to_supabase(
    image_data: bytes,
    filename: str,
    save_local: bool = True
) -> Optional[Tuple[str, str]]:
    """上传图片到Supabase bucket，可选保存本地副本"""
    user_id = current_user_id.get() or USER_ID
    storage_path = f"{user_id}/images/{filename}"

    # 保存本地副本（无论Supabase是否可用）
    local_path = None
    if save_local:
        base = Path(__file__).parent.parent.parent / BASE_DIR
        local_folder = base / "images"
        local_folder.mkdir(parents=True, exist_ok=True)
        local_path = local_folder / filename
        with open(local_path, "wb") as f:
            f.write(image_data)
        print(f"💾 本地保存: {local_path}")

    supabase_client = _init_supabase()
    if not supabase_client:
        print("⚠️  Supabase不可用，仅保存本地副本")
        return (storage_path, str(local_path)) if local_path else None

    try:
        print(f"☁️  上传: {storage_path}")

        try:
            supabase_client.storage.from_("files").upload(
                storage_path, image_data,
                file_options={"cache_control": "3600"}
            )
            print("✅ 上传成功")
        except Exception as upload_error:
            error_str = str(upload_error)
            if ("409" in error_str or "Duplicate" in error_str or
                    "already exists" in error_str):
                print("⚠️  文件已存在，更新...")
                supabase_client.storage.from_("files").update(
                    storage_path, image_data,
                    file_options={"cache_control": "3600"}
                )
                print("✅ 更新成功")
            else:
                raise

        existing = (
            supabase_client.table("user_images")
            .select("id")
            .eq("user_id", user_id)
            .eq("storage_path", storage_path)
            .execute()
        )

        if existing.data:
            supabase_client.table("user_images").update({
                "filename": filename,
                "file_size": len(image_data),
                "mime_type": "image/jpeg"
            }).eq("user_id", user_id).eq(
                "storage_path", storage_path
            ).execute()
        else:
            supabase_client.table("user_images").insert({
                "user_id": user_id,
                "storage_path": storage_path,
                "filename": filename,
                "file_size": len(image_data),
                "mime_type": "image/jpeg"
            }).execute()

        signed_url_response = (
            supabase_client.storage.from_("files")
            .create_signed_url(storage_path, expires_in=3600)
        )

        public_url = None
        if isinstance(signed_url_response, dict):
            public_url = (
                signed_url_response.get("signedURL") or
                signed_url_response.get("signedUrl") or
                signed_url_response.get("signed_url") or
                signed_url_response.get("url")
            )
        elif isinstance(signed_url_response, str):
            public_url = signed_url_response

        return (storage_path, public_url)
    except Exception as e:
        print(f"❌ 上传异常: {type(e).__name__}: {str(e)}")
        return None


async def get_image_url_from_asset_id(asset_id: str) -> Optional[str]:
    """从asset_id获取图片URL"""
    supabase_client = _init_supabase()
    if not supabase_client:
        raise RuntimeError("Supabase未配置")
    try:
        response = (
            supabase_client.table("user_images")
            .select("storage_path")
            .eq("id", asset_id)
            .single()
            .execute()
        )
        if not response.data:
            raise Exception("文件不存在")
        storage_path = response.data.get("storage_path")

        signed_url_response = (
            supabase_client.storage.from_("files")
            .create_signed_url(storage_path, expires_in=3600)
        )

        if isinstance(signed_url_response, dict):
            signed_url = (
                signed_url_response.get("signedURL") or
                signed_url_response.get("signedUrl")
            )
            if signed_url:
                return signed_url
        elif isinstance(signed_url_response, str):
            return signed_url_response

        raise Exception(f"生成URL失败: {type(signed_url_response)}")
    except Exception as e:
        print(f"❌ 获取URL异常: {type(e).__name__}: {str(e)}")
        return None


def ensure_folder_structure(folder_type: str) -> Path:
    """确保文件夹结构存在

    Args:
        folder_type: 文件夹类型 ("image", "video", "audio" 等)

    Returns:
        Path: 创建的文件夹路径
    """
    base = Path(__file__).parent.parent.parent / BASE_DIR
    folder = base / f"{folder_type}s"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


async def save_to_supabase(
    file_path: Path,
    folder_type: str
) -> Optional[Tuple[str, str]]:
    """上传文件到Supabase并保存元数据

    Args:
        file_path: 本地文件路径
        folder_type: 文件夹类型 ("image", "video", "audio" 等)

    Returns:
        Optional[Tuple[str, str]]: (storage_path, public_url) 或 None
    """
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return None

    with open(file_path, "rb") as f:
        file_data = f.read()

    filename = file_path.name
    return await save_image_to_supabase(
        image_data=file_data,
        filename=filename,
        save_local=False  # 已经有本地文件了
    )
