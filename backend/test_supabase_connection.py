"""测试 Supabase 连接 - 详细诊断"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("Supabase 连接测试")
print("="*60)

# 直接从环境变量读取
import os
from dotenv import load_dotenv

# 加载 .env
env_path = Path(__file__).parent.parent / ".env"
print(f"\n加载 .env 文件: {env_path}")
print(f"文件存在: {env_path.exists()}")

load_dotenv(dotenv_path=env_path, override=True)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SECRET_KEY")

print(f"\nSUPABASE_URL: {url}")
print(f"SUPABASE_SECRET_KEY: {key[:20]}... (长度: {len(key)})")

# 测试连接
print("\n" + "="*60)
print("测试 Supabase 客户端")
print("="*60)

try:
    from supabase import create_client, Client

    print(f"\n创建客户端...")
    print(f"  URL: {url}")
    print(f"  Key: {key[:15]}...")

    client: Client = create_client(url, key)
    print("✅ 客户端创建成功")

    # 测试存储
    print("\n测试存储访问...")
    try:
        buckets = client.storage.list_buckets()
        print(f"✅ 存储访问成功！找到 {len(buckets)} 个 buckets:")
        for bucket in buckets:
            print(f"  - {bucket.name} (id: {bucket.id})")
    except Exception as e:
        print(f"❌ 存储访问失败: {type(e).__name__}: {e}")

    # 测试数据库
    print("\n测试数据库访问...")
    try:
        # 尝试查询 user_files 表
        result = client.table("user_files").select("id").limit(1).execute()
        print(f"✅ 数据库访问成功！")
    except Exception as e:
        print(f"⚠️  数据库查询: {type(e).__name__}: {e}")

except Exception as e:
    print(f"\n❌ 连接失败: {type(e).__name__}")
    print(f"错误详情: {e}")

    # 打印完整的错误堆栈
    import traceback
    print("\n完整错误堆栈:")
    traceback.print_exc()
