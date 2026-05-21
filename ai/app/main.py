"""FastAPI main application for ScopeWise."""

# Patch sqlite3 BEFORE any chromadb/langchain_chroma import.
# ChromaDB requires sqlite3 >= 3.35.0; pysqlite3-binary ships a newer version.
import sys
try:
    import pysqlite3  # type: ignore[import-untyped]
    sys.modules["sqlite3"] = pysqlite3
except ImportError:
    pass

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.service import AgentService
from app.config import get_settings
from app.routes.pipeline import router as pipeline_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown.
    
    During startup: Initialize AgentService and call warmup() to verify LLM
    and templates are available.
    """
    # Route app.* INFO logs to stderr without clobbering uvicorn's logging config.
    app_root = logging.getLogger("app")
    if not app_root.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(
            logging.Formatter("%(levelname)s [%(name)s] %(message)s")
        )
        app_root.addHandler(handler)
        app_root.setLevel(logging.INFO)
        app_root.propagate = False

    # Startup
    settings = get_settings()
    agent_service = AgentService(settings)
    agent_service.warmup()
    app.state.agent_service = agent_service
    
    yield
    
    # Shutdown
    # Add cleanup logic here if needed


app = FastAPI(
    title="ScopeWise API",
    description="Modern Python learning project with optimal tech stack",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(pipeline_router, prefix="/api")


@app.get("/")
async def test() -> dict[str, str]:
    """Test endpoint."""
    return {"message": "Hello from ScopeWise!", "version": "0.1.0"}

@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
