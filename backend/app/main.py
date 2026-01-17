from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Import and register routers
from app.routers import assets, storybooks

app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(storybooks.router, prefix="/api/storybooks", tags=["storybooks"])

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
