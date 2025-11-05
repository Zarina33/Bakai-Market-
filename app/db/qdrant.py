"""
Qdrant client for vector embeddings storage and search.
"""
import numpy as np
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient as QdrantClientSDK
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from app.config import settings


class QdrantClient:
    """Qdrant vector database client."""
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        collection_name: str = None,
        vector_size: int = None,
    ):
        """
        Initialize Qdrant client.
        
        Args:
            host: Qdrant host (default from settings)
            port: Qdrant port (default from settings)
            collection_name: Collection name (default from settings)
            vector_size: Vector embedding size (default from settings)
        """
        self.host = host or settings.qdrant_host
        self.port = port or settings.qdrant_port
        self.collection_name = collection_name or settings.qdrant_collection_name
        self.vector_size = vector_size or settings.qdrant_vector_size
        
        # Initialize client
        self.client = QdrantClientSDK(host=self.host, port=self.port)
    
    def create_collection(self, recreate: bool = False) -> None:
        """
        Create vector collection.
        
        Args:
            recreate: If True, delete existing collection and create new one
        """
        if recreate and self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
        
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                ),
            )
    
    def add_vectors(
        self,
        vectors: List[np.ndarray],
        ids: List[str],
        payloads: List[Dict[str, Any]] = None,
    ) -> None:
        """
        Add vectors to collection.
        
        Args:
            vectors: List of embedding vectors
            ids: List of unique IDs
            payloads: List of metadata dictionaries
        """
        if payloads is None:
            payloads = [{}] * len(vectors)
        
        points = [
            PointStruct(
                id=idx,
                vector=vector.tolist() if isinstance(vector, np.ndarray) else vector,
                payload=payload,
            )
            for idx, (vector, payload) in enumerate(zip(vectors, payloads), start=1)
        ]
        
        self.client.upsert(collection_name=self.collection_name, points=points)
    
    def search(
        self,
        query_vector: np.ndarray,
        limit: int = None,
        score_threshold: float = None,
        filter_conditions: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results (default from settings)
            score_threshold: Minimum similarity score (default from settings)
            filter_conditions: Optional metadata filters
            
        Returns:
            List of search results with scores and payloads
        """
        limit = limit or settings.default_search_limit
        score_threshold = score_threshold or settings.similarity_threshold
        
        # Prepare filter if provided
        query_filter = None
        if filter_conditions:
            conditions = [
                FieldCondition(key=key, match=MatchValue(value=value))
                for key, value in filter_conditions.items()
            ]
            query_filter = Filter(must=conditions)
        
        # Convert numpy array to list
        vector = query_vector.tolist() if isinstance(query_vector, np.ndarray) else query_vector
        
        # Perform search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )
        
        # Format results
        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload,
            }
            for result in results
        ]
    
    def delete_vectors(self, ids: List[str]) -> None:
        """
        Delete vectors by IDs.
        
        Args:
            ids: List of vector IDs to delete
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=ids,
        )
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get collection information.
        
        Returns:
            Dictionary with collection stats
        """
        info = self.client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status,
        }

