"""
PostgreSQL client for product metadata storage.
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, List, Any
from contextlib import contextmanager

from app.config import settings


class PostgresClient:
    """PostgreSQL database client."""
    
    def __init__(self, connection_url: str = None):
        """
        Initialize PostgreSQL client.
        
        Args:
            connection_url: PostgreSQL connection URL (default from settings)
        """
        self.connection_url = connection_url or settings.database_url
        self._connection = None
    
    def connect(self) -> None:
        """Establish database connection."""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(self.connection_url)
    
    def close(self) -> None:
        """Close database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
    
    @contextmanager
    def get_cursor(self, dict_cursor: bool = True):
        """
        Context manager for database cursor.
        
        Args:
            dict_cursor: Use RealDictCursor for dict-like results
            
        Yields:
            Database cursor
        """
        self.connect()
        cursor_factory = RealDictCursor if dict_cursor else None
        cursor = self._connection.cursor(cursor_factory=cursor_factory)
        try:
            yield cursor
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise
        finally:
            cursor.close()
    
    def execute(self, query: str, params: tuple = None) -> None:
        """
        Execute a query without returning results.
        
        Args:
            query: SQL query
            params: Query parameters
        """
        with self.get_cursor(dict_cursor=False) as cursor:
            cursor.execute(query, params)
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Dictionary with row data or None
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Fetch all rows.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of dictionaries with row data
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def create_tables(self) -> None:
        """Create necessary database tables."""
        create_products_table = """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            external_id VARCHAR(255) UNIQUE NOT NULL,
            title VARCHAR(500) NOT NULL,
            description TEXT,
            category VARCHAR(255),
            price DECIMAL(10, 2),
            currency VARCHAR(10),
            image_url TEXT,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_products_external_id ON products(external_id);
        CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
        CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);
        """
        
        create_search_logs_table = """
        CREATE TABLE IF NOT EXISTS search_logs (
            id SERIAL PRIMARY KEY,
            query_type VARCHAR(50) NOT NULL,
            query_text TEXT,
            query_image_url TEXT,
            results_count INTEGER,
            execution_time_ms INTEGER,
            user_id VARCHAR(255),
            session_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_search_logs_created_at ON search_logs(created_at);
        CREATE INDEX IF NOT EXISTS idx_search_logs_user_id ON search_logs(user_id);
        """
        
        self.execute(create_products_table)
        self.execute(create_search_logs_table)

