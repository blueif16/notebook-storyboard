"""存储服务 - Supabase核心功能"""
from pathlib import Path
from typing import Optional, Any, tuple
from contextvars import ContextVar
from dotenv import load_dotenv
from ..config import SUPABASE_URL, SUPABASE_SERVICE_KEY, USER_ID, BASE_DIR

load_dotenv()

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
        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
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
) -> Optional[tuple[str, str]]:
    """上传图片到Supabase bucket，可选保存本地副本"""
    supabase_client = _init_supabase()
    if not supabase_client:
        return None
    try:
        user_id = current_user_id.get() or USER_ID
        storage_path = f"{user_id}/images/{filename}"

        # 保存本地副本
        if save_local:
            base = Path(__file__).parent.parent.parent / BASE_DIR
            local_folder = base / "images"
            local_folder.mkdir(parents=True, exist_ok=True)
            local_path = local_folder / filename
            with open(local_path, "wb") as f:
                f.write(image_data)
            print(f"💾 本地保存: {local_path}")

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
            supabase_client.table("user_files")
            .select("id")
            .eq("user_id", user_id)
            .eq("storage_path", storage_path)
            .execute()
        )

        if existing.data:
            supabase_client.table("user_files").update({
                "filename": filename,
                "file_size": len(image_data),
                "mime_type": "image/jpeg"
            }).eq("user_id", user_id).eq(
                "storage_path", storage_path
            ).execute()
        else:
            supabase_client.table("user_files").insert({
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
            supabase_client.table("user_files")
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
