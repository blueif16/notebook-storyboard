"""检查 .env 文件路径和加载"""
from pathlib import Path
from dotenv import load_dotenv
import os

print("="*60)
print("检查 .env 文件路径")
print("="*60)

# 检查 config.py 的路径计算
config_file = Path(__file__).parent / "app" / "config.py"
print(f"\nconfig.py 位置: {config_file}")

# 模拟 config.py 的路径计算
parent_dir = Path(__file__).parent.parent
env_path = parent_dir / ".env"
print(f"\nconfig.py 计算的 .env 路径: {env_path}")
print(f".env 文件存在: {env_path.exists()}")

if env_path.exists():
    print(f".env 文件大小: {env_path.stat().st_size} bytes")

    # 尝试加载
    print("\n尝试加载 .env 文件...")
    load_dotenv(dotenv_path=env_path, override=True)

    print(f"\nSUPABASE_URL: {os.getenv('SUPABASE_URL')}")
    print(f"SUPABASE_SECRET_KEY: {'SET' if os.getenv('SUPABASE_SECRET_KEY') else 'NOT SET'}")
    if os.getenv('SUPABASE_SECRET_KEY'):
        key = os.getenv('SUPABASE_SECRET_KEY')
        print(f"  长度: {len(key)}")
        print(f"  前缀: {key[:20]}...")

# 检查 storage_service.py 的路径计算
print("\n" + "="*60)
print("检查 storage_service.py 的路径计算")
print("="*60)

# 模拟 storage_service.py 的路径计算
storage_service_path = Path(__file__).parent / "app" / "services" / "storage_service.py"
parent_dir2 = storage_service_path.resolve().parent.parent.parent.parent
env_path2 = parent_dir2 / ".env"
print(f"\nstorage_service.py 计算的 .env 路径: {env_path2}")
print(f".env 文件存在: {env_path2.exists()}")
