"""AG-UI FastAPI Server for Storybook"""
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ag_ui.core import RunAgentInput
from .adapter import run_storybook_stream, SSE_CONTENT_TYPE

app = FastAPI(title="Storybook AG-UI", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://localhost:3847", "http://127.0.0.1:3847"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/storybook")
async def storybook_endpoint(input_data: RunAgentInput):
    """Main AG-UI endpoint - streams storybook generation."""
    return StreamingResponse(run_storybook_stream(input_data), media_type=SSE_CONTENT_TYPE)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "storybook-ag-ui", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
