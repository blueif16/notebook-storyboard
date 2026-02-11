#!/usr/bin/env python3
"""
Server startup script with UNBUFFERED output
"""
import os
import sys
from pathlib import Path

# CRITICAL: Force unbuffered output for real-time logging
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)
os.environ['PYTHONUNBUFFERED'] = '1'

# Get the backend directory (where this script is located)
backend_dir = Path(__file__).parent.absolute()

# Change to backend directory
os.chdir(backend_dir)

# Add backend to Python path
sys.path.insert(0, str(backend_dir))

# Set PYTHONPATH environment variable for subprocesses
os.environ['PYTHONPATH'] = f"{backend_dir}:{os.environ.get('PYTHONPATH', '')}"

# Now run uvicorn
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8005))

    print("="*80)
    print("🚀 Starting Main Backend Server with UNBUFFERED output")
    print("="*80)

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=[str(backend_dir)],
        log_level="info"
    )
