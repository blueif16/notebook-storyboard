"""Check Supabase configuration"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import SUPABASE_URL, SUPABASE_SECRET_KEY

print("Supabase Configuration Check:")
print(f"SUPABASE_URL: {SUPABASE_URL[:50] if SUPABASE_URL else 'NOT SET'}...")
print(f"SUPABASE_SECRET_KEY: {'SET (' + str(len(SUPABASE_SECRET_KEY)) + ' chars)' if SUPABASE_SECRET_KEY else 'NOT SET'}")

if SUPABASE_SECRET_KEY:
    print(f"Key starts with: {SUPABASE_SECRET_KEY[:20]}...")
    print(f"Key type: {type(SUPABASE_SECRET_KEY)}")

    # Try to initialize
    from app.services.storage_service import _init_supabase
    result = _init_supabase()
    if result:
        print("✅ Supabase initialized successfully!")
    else:
        print("❌ Supabase initialization failed")
