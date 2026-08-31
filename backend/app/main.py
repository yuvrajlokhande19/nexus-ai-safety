import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .api import websocket, experiments

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Nexus AI Safety Research Platform")
    os.makedirs(settings.experiments_dir, exist_ok=True)
    os.makedirs(settings.exports_dir, exist_ok=True)
    
    # Initialize ChromaDB if available
    from .services.memory_store import memory_store
    logger.info("Memory store initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title="Nexus AI Safety Research Platform",
    description="Multi-agent persona system for AI alignment research",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(websocket.router)
app.include_router(experiments.router)

# Health check
@app.get("/health")
async def health_check():
    from .services.llm_router import llm_router
    model_info = llm_router.get_model_info()
    return {
        "status": "healthy",
        "models": model_info
    }


@app.get("/")
async def root():
    return {
        "name": "Nexus AI Safety Research Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws/{experiment_id}"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)