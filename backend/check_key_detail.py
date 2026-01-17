"""详细检查 Supabase key"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import SUPABASE_URL, SUPABASE_SECRET_KEY

print("="*60)
print("Supabase Key 详细检查")
print("="*60)

if SUPABASE_SECRET_KEY:
    print(f"\nKey 长度: {len(SUPABASE_SECRET_KEY)}")
    print(f"Key 完整内容: {SUPABASE_SECRET_KEY}")
    print(f"\nKey 字符分析:")
    print(f"  - 包含空格: {' ' in SUPABASE_SECRET_KEY}")
    print(f"  - 包含换行: {'\\n' in SUPABASE_SECRET_KEY}")
    print(f"  - 包含制表符: {'\\t' in SUPABASE_SECRET_KEY}")
    print(f"  - 前后有空白: {SUPABASE_SECRET_KEY != SUPABASE_SECRET_KEY.strip()}")

    if SUPABASE_SECRET_KEY != SUPABASE_SECRET_KEY.strip():
        print(f"\n⚠️  Key 前后有空白字符！")
        print(f"  原始: '{SUPABASE_SECRET_KEY}'")
        print(f"  清理后: '{SUPABASE_SECRET_KEY.strip()}'")

print(f"\nURL: {SUPABASE_URL}")

# 尝试用清理后的 key 连接
print("\n" + "="*60)
print("尝试用清理后的 key 连接")
print("="*60)

try:
    from supabase import create_client
    clean_key = SUPABASE_SECRET_KEY.strip() if SUPABASE_SECRET_KEY else None

    if clean_key:
        print(f"清理后的 key 长度: {len(clean_key)}")
        client = create_client(SUPABASE_URL, clean_key)
        print("✅ 连接成功！")

        # 测试存储访问
        buckets = client.storage.list_buckets()
        print(f"✅ 找到 {len(buckets)} 个 buckets")
except Exception as e:
    print(f"❌ 连接失败: {e}")
