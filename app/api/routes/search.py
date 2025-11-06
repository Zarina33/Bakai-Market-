"""
Search endpoints for visual and text search.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List, Optional
from PIL import Image
import io

from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.models.clip_model import CLIPModel
from app.db.qdrant import QdrantManager
from app.db import postgres
from app.config import settings

router = APIRouter()

# Initialize clients (in production, use dependency injection)
clip_model = None
qdrant_client = None


def get_clip_model() -> CLIPModel:
    """Get or initialize CLIP model."""
    global clip_model
    if clip_model is None:
        clip_model = CLIPModel()
    return clip_model


def get_qdrant_client() -> QdrantManager:
    """Get or initialize Qdrant client."""
    global qdrant_client
    if qdrant_client is None:
        qdrant_client = QdrantManager()
    return qdrant_client


@router.post("/search/text", response_model=SearchResponse)
async def search_by_text(
    query: str = Query(..., description="Search query text"),
    limit: int = Query(default=20, le=100, description="Maximum number of results"),
    threshold: float = Query(default=0.5, ge=0.0, le=1.0, description="Similarity threshold"),
) -> SearchResponse:
    """
    Search products by text query.
    
    Args:
        query: Text search query
        limit: Maximum number of results
        threshold: Minimum similarity threshold
        
    Returns:
        Search results with product information
    """
    try:
        # Encode text query
        model = get_clip_model()
        query_embedding = model.encode_text(query)
        
        # Search in Qdrant
        qdrant = get_qdrant_client()
        vector_results = qdrant.search(
            query_vector=query_embedding,
            limit=limit,
            score_threshold=threshold,
        )
        
        # Get product details from PostgreSQL
        if vector_results:
            product_ids = [result["payload"].get("product_id") for result in vector_results]
            pg = get_postgres_client()
            
            results = []
            for vector_result in vector_results:
                product_id = vector_result["payload"].get("product_id")
                product = pg.fetch_one(
                    "SELECT * FROM products WHERE external_id = %s",
                    (product_id,)
                )
                
                if product:
                    results.append(
                        SearchResult(
                            product_id=product["external_id"],
                            title=product["title"],
                            description=product.get("description"),
                            image_url=product.get("image_url"),
                            score=vector_result["score"],
                            metadata=product.get("metadata"),
                        )
                    )
            
            return SearchResponse(
                query=query,
                query_type="text",
                results=results,
                total=len(results),
            )
        
        return SearchResponse(query=query, query_type="text", results=[], total=0)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/search/image", response_model=SearchResponse)
async def search_by_image(
    image: UploadFile = File(..., description="Query image file"),
    limit: int = Query(default=20, le=100, description="Maximum number of results"),
    threshold: float = Query(default=0.5, ge=0.0, le=1.0, description="Similarity threshold"),
) -> SearchResponse:
    """
    Search products by image.
    
    Args:
        image: Uploaded image file
        limit: Maximum number of results
        threshold: Minimum similarity threshold
        
    Returns:
        Search results with product information
    """
    try:
        # Validate image format
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_data = await image.read()
        pil_image = Image.open(io.BytesIO(image_data)).convert("RGB")
        
        # Encode image
        model = get_clip_model()
        query_embedding = model.encode_image(pil_image)
        
        # Search in Qdrant
        qdrant = get_qdrant_client()
        vector_results = qdrant.search(
            query_vector=query_embedding,
            limit=limit,
            score_threshold=threshold,
        )
        
        # Get product details from PostgreSQL
        if vector_results:
            pg = get_postgres_client()
            
            results = []
            for vector_result in vector_results:
                product_id = vector_result["payload"].get("product_id")
                product = pg.fetch_one(
                    "SELECT * FROM products WHERE external_id = %s",
                    (product_id,)
                )
                
                if product:
                    results.append(
                        SearchResult(
                            product_id=product["external_id"],
                            title=product["title"],
                            description=product.get("description"),
                            image_url=product.get("image_url"),
                            score=vector_result["score"],
                            metadata=product.get("metadata"),
                        )
                    )
            
            return SearchResponse(
                query=image.filename,
                query_type="image",
                results=results,
                total=len(results),
            )
        
        return SearchResponse(
            query=image.filename,
            query_type="image",
            results=[],
            total=0,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

