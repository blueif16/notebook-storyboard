"""Detailed Supabase diagnostic"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import SUPABASE_URL, SUPABASE_SECRET_KEY

print("="*60)
print("Supabase Diagnostic")
print("="*60)
print(f"\nSUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_SECRET_KEY length: {len(SUPABASE_SECRET_KEY) if SUPABASE_SECRET_KEY else 0}")
print(f"Key prefix: {SUPABASE_SECRET_KEY[:15] if SUPABASE_SECRET_KEY else 'N/A'}...")

if SUPABASE_URL and SUPABASE_SECRET_KEY:
    print("\n" + "="*60)
    print("Testing Supabase Connection")
    print("="*60)

    try:
        from supabase import create_client
        print("✅ Supabase library imported")

        print(f"\nAttempting to create client...")
        client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
        print("✅ Client created")

        # Try a simple operation
        print("\nTesting storage access...")
        try:
            buckets = client.storage.list_buckets()
            print(f"✅ Storage accessible! Found {len(buckets)} buckets")
            for bucket in buckets:
                print(f"  - {bucket.name}")
        except Exception as e:
            print(f"❌ Storage access failed: {e}")

    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}: {e}")
else:
    print("\n❌ Missing configuration")
