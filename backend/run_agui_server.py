#!/usr/bin/env python3
"""
AG-UI Server startup script
"""
import os
import sys
from pathlib import Path

# Get the backend directory
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

    host = os.getenv("AGUI_HOST", "0.0.0.0")
    port = int(os.getenv("AGUI_PORT", 8001))

    uvicorn.run(
        "app.ag_ui.server:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=[str(backend_dir)]
    )
