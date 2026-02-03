from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables from parent folder (project root)
parent_dir = Path(__file__).resolve().parent.parent.parent
env_path = parent_dir / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(
    title="HyperBookLM Backend API",
    description="Backend API for HyperBookLM application",
    version="1.0.0"
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "HyperBookLM Backend API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to show all registered routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods)
            })
    return {"routes": routes}

# Clear agent cache on startup (for development hot reload)
print("[MAIN] Clearing agent cache...")
from app.agents import AgentCache
AgentCache.clear_cache()
print("[MAIN] ✓ Agent cache cleared")

# Import and register routers
print("[MAIN] Importing routers...")
from app.routers import assets, storybooks

print("[MAIN] Registering asset and storybook routers...")
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(storybooks.router, prefix="/api/storybooks", tags=["storybooks"])

# AG-UI Streaming Endpoint (merged from separate server)
print("[MAIN] Importing AG-UI components...")
try:
    from ag_ui.core import RunAgentInput
    from app.ag_ui.adapter import run_storybook_stream, SSE_CONTENT_TYPE
    print("[MAIN] ✓ AG-UI imports successful")
except Exception as e:
    print(f"[MAIN] ✗ AG-UI import failed: {e}")
    import traceback
    traceback.print_exc()
    raise

print("[MAIN] Registering /storybook endpoint...")

@app.post("/storybook")
async def storybook_streaming_endpoint(input_data: RunAgentInput):
    """AG-UI streaming endpoint for storybook generation."""
    print(f"[MAIN] /storybook endpoint called with thread_id: {getattr(input_data, 'thread_id', None)}")
    return StreamingResponse(run_storybook_stream(input_data), media_type=SSE_CONTENT_TYPE)

print("[MAIN] ✓ /storybook endpoint registered")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
