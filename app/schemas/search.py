"""
Search schemas.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class SearchRequest(BaseModel):
    """Search request schema."""
    query: str = Field(..., description="Search query (text or image URL)")
    limit: int = Field(default=20, le=100, description="Maximum number of results")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Similarity threshold")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional metadata filters")


class SearchResult(BaseModel):
    """Single search result."""
    product_id: str = Field(..., description="Product ID")
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    image_url: Optional[str] = Field(None, description="Product image URL")
    score: float = Field(..., description="Similarity score")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str = Field(..., description="Original query")
    query_type: str = Field(..., description="Query type (text/image)")
    results: List[SearchResult] = Field(default=[], description="Search results")
    total: int = Field(..., description="Total number of results")

