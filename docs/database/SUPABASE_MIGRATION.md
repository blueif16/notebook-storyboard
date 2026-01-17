# Supabase API Key Migration Guide

## Overview

This project has been updated to use Supabase's **new recommended secret key format** (`sb_secret_...`) instead of the legacy JWT-based `service_role` key.

## What Changed?

### Before (Legacy)
```env
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### After (New - Recommended)
```env
SUPABASE_SECRET_KEY=sb_secret_your_secret_key_here
```

## Why Migrate?

The new secret key format provides several advantages:

1. **Easy Rotation**: Change keys without downtime or JWT secret rotation
2. **Better Security**: Cannot be used in browsers (returns HTTP 401)
3. **Independent**: Not tied to JWT secret or other authentication tokens
4. **Flexible**: Create multiple secret keys for different backend components
5. **Reversible**: Can delete and recreate without affecting other services

## Migration Steps

### Step 1: Get Your New Secret Key

1. Go to your Supabase Dashboard
2. Navigate to: **Project Settings** > **API** > **API Keys**
3. Click **"Create new API Keys"**
4. Copy the value from the **"Secret key"** section (starts with `sb_secret_`)

### Step 2: Update Your .env File

Add the new key to your `.env` file:

```env
# New secret key (recommended)
SUPABASE_SECRET_KEY=sb_secret_your_actual_key_here

# Keep the old key temporarily for rollback if needed
# SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 3: Test Your Application

The code has backward compatibility built-in. It will:
1. First try to use `SUPABASE_SECRET_KEY`
2. Fall back to `SUPABASE_SERVICE_KEY` if the new key isn't set

Test your application to ensure everything works:

```bash
cd backend
python -m app.main
```

### Step 4: Remove Old Key (Optional)

Once you've confirmed everything works, you can remove the old `SUPABASE_SERVICE_KEY` from your `.env` file.

## Code Changes Made

### 1. config.py
```python
# Now uses SUPABASE_SECRET_KEY with backward compatibility
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
if not SUPABASE_SECRET_KEY:
    SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SERVICE_KEY")
```

### 2. storage_service.py
```python
# Updated import and initialization
from ..config import SUPABASE_URL, SUPABASE_SECRET_KEY
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
```

## Security Best Practices

### DO:
- ✅ Use secret keys only in backend services (servers, Edge Functions, APIs)
- ✅ Store secret keys in environment variables
- ✅ Use separate secret keys for different backend components
- ✅ Rotate keys immediately if compromised
- ✅ Use encrypted storage for keys in files

### DON'T:
- ❌ Never expose secret keys in frontend code
- ❌ Never commit secret keys to source control
- ❌ Never use secret keys in browsers (even localhost)
- ❌ Never send keys via chat, email, or SMS
- ❌ Never log full secret keys (max 6 characters if needed)

## Rollback Plan

If you need to rollback:

1. The old `SUPABASE_SERVICE_KEY` still works
2. Simply remove `SUPABASE_SECRET_KEY` from your `.env`
3. The code will automatically fall back to the old key

## FAQ

### Can I use both keys at the same time?
Yes! The code has backward compatibility. It will prefer the new secret key but fall back to the old service_role key.

### Do I need to update my database or storage buckets?
No. The keys are just different authentication methods. Your data and permissions remain unchanged.

### What about the `anon` key for frontend?
For frontend applications, Supabase now recommends using the **publishable key** (`sb_publishable_...`) instead of the `anon` JWT key. However, this backend service only uses secret keys.

### How do I rotate a secret key?
1. Create a new secret key in the Supabase dashboard
2. Update your `.env` file with the new key
3. Restart your application
4. Delete the old secret key from the dashboard

### What if my secret key is leaked?
1. Immediately create a new secret key
2. Update your application
3. Delete the compromised key from the dashboard
4. Review your security practices

## Additional Resources

- [Supabase API Keys Documentation](https://supabase.com/docs/guides/api/api-keys)
- [Security Best Practices](https://supabase.com/docs/guides/api/api-keys#best-practices-for-handling-secret-keys)
- [Project Dashboard](https://supabase.com/dashboard)

## Support

If you encounter any issues during migration, check:
1. The key format is correct (`sb_secret_...`)
2. The key is from the correct Supabase project
3. Environment variables are loaded properly
4. No typos in the `.env` file
