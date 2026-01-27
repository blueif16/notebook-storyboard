#!/usr/bin/env python3
"""
Server startup script that ensures proper working directory for uvicorn reload.
"""
import os
import sys
from pathlib import Path

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
    port = int(os.getenv("API_PORT", 8000))

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=[str(backend_dir)]
    )
