"""直接测试 Supabase API key"""
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SECRET_KEY")

print("="*60)
print("直接 HTTP 测试 Supabase API")
print("="*60)
print(f"\nURL: {url}")
print(f"Key: {key[:20]}... (长度: {len(key)})")

# 测试 REST API
print("\n" + "="*60)
print("测试 REST API")
print("="*60)

try:
    # 尝试访问 REST API
    rest_url = f"{url}/rest/v1/"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}"
    }

    print(f"\n请求 URL: {rest_url}")
    print(f"Headers: apikey={key[:15]}..., Authorization=Bearer {key[:15]}...")

    response = httpx.get(rest_url, headers=headers, timeout=10.0)
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应内容: {response.text[:200]}")

    if response.status_code == 200:
        print("\n✅ REST API 访问成功！")
    else:
        print(f"\n❌ REST API 访问失败")

except Exception as e:
    print(f"\n❌ 请求失败: {type(e).__name__}: {e}")

# 测试 Storage API
print("\n" + "="*60)
print("测试 Storage API")
print("="*60)

try:
    storage_url = f"{url}/storage/v1/bucket"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}"
    }

    print(f"\n请求 URL: {storage_url}")

    response = httpx.get(storage_url, headers=headers, timeout=10.0)
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应内容: {response.text[:500]}")

    if response.status_code == 200:
        print("\n✅ Storage API 访问成功！")
        import json
        buckets = json.loads(response.text)
        print(f"找到 {len(buckets)} 个 buckets:")
        for bucket in buckets:
            print(f"  - {bucket.get('name')} (id: {bucket.get('id')})")
    else:
        print(f"\n❌ Storage API 访问失败")

except Exception as e:
    print(f"\n❌ 请求失败: {type(e).__name__}: {e}")
