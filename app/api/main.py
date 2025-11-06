"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.api.routes import search, health, products
from app.models.clip_model import CLIPEmbedder
from app.db.qdrant import QdrantManager


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        description="Visual Search API using CLIP embeddings",
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers (search router already has prefix)
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(search.router, tags=["search"])
    app.include_router(products.router, prefix="/api/v1", tags=["products"])
    
    return app


app = create_app()


@app.on_event("startup")
async def startup_event():
    """Инициализация при старте приложения."""
    logger.info("=" * 60)
    logger.info("Starting Visual Search API...")
    logger.info("=" * 60)
    
    try:
        # Инициализация CLIP embedder
        logger.info("Initializing CLIP embedder...")
        search.clip_embedder = CLIPEmbedder(device="auto")
        logger.success(f"✅ CLIP embedder initialized (device={search.clip_embedder.device})")
        
        # Инициализация Qdrant manager
        logger.info("Initializing Qdrant manager...")
        search.qdrant_manager = QdrantManager(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            collection_name=settings.qdrant_collection_name
        )
        
        # Проверка коллекции
        if await search.qdrant_manager.collection_exists():
            info = await search.qdrant_manager.get_collection_info()
            logger.success(f"✅ Qdrant connected: {info['points_count']} vectors in collection")
        else:
            logger.warning("⚠️  Qdrant collection does not exist. Please run load_demo_products.py first.")
        
        logger.info("=" * 60)
        logger.success("✅ Startup complete! API is ready.")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при остановке приложения."""
    logger.info("Shutting down Visual Search API...")
    
    # Cleanup if needed
    if search.qdrant_manager:
        search.qdrant_manager.close()
    
    logger.info("✅ Shutdown complete")

