# Database Setup Guide

This guide explains how to set up and use the PostgreSQL and Qdrant databases for the visual search system.

## Quick Start

### 1. Install Dependencies

```bash
# Using Poetry
poetry install

# Or using pip
pip install sqlalchemy[asyncio] asyncpg qdrant-client loguru
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=visual_search
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=product_embeddings
QDRANT_VECTOR_SIZE=512
```

### 3. Start Database Services

#### Using Docker Compose (Recommended)

```bash
# Start PostgreSQL and Qdrant
docker-compose up -d postgres qdrant

# Check status
docker-compose ps
```

#### Manual Setup

**PostgreSQL:**
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb visual_search
```

**Qdrant:**
```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant

# Or download binary from https://qdrant.tech/
```

### 4. Initialize Databases

```bash
# Run initialization script
python scripts/init_databases.py
```

Expected output:
```
============================================================
🚀 DATABASE INITIALIZATION SCRIPT
============================================================

📦 Project: visual-search-project
🔖 Version: 0.1.0
🔧 Environment: Development

============================================================
📊 INITIALIZING POSTGRESQL DATABASE
============================================================

🔗 Connecting to PostgreSQL...
   Host: localhost
   Port: 5432
   Database: visual_search
   User: postgres

📋 Creating tables...

✅ PostgreSQL initialized successfully!

📊 Tables created:
   • products
   • search_logs

============================================================
🔍 INITIALIZING QDRANT VECTOR DATABASE
============================================================

🔗 Connecting to Qdrant...
   Host: localhost
   Port: 6333
   Collection: product_embeddings

📦 Creating collection...
   Vector size: 512
   Distance metric: Cosine

✅ Qdrant initialized successfully!

📊 Collection info:
   • Name: product_embeddings
   • Vector size: 512
   • Distance: Cosine
   • Points count: 0
   • Status: green

============================================================
📋 INITIALIZATION SUMMARY
============================================================

✅ PostgreSQL: SUCCESS
✅ Qdrant: SUCCESS

🎉 All databases initialized successfully!

📝 Next steps:
   1. Load sample data: python scripts/load_sample_data.py
   2. Start the API server: make run
   3. Test the API: python tests/test_api.py

============================================================
```

## Database Schemas

### PostgreSQL Tables

#### products
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price NUMERIC(10, 2),
    currency VARCHAR(10),
    image_url VARCHAR(1000),
    product_metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_external_id ON products(external_id);
CREATE INDEX idx_products_category ON products(category);
```

#### search_logs
```sql
CREATE TABLE search_logs (
    id SERIAL PRIMARY KEY,
    query_type VARCHAR(50) NOT NULL,
    product_id VARCHAR(255),
    similarity_score FLOAT,
    results_count INTEGER,
    search_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_search_logs_created_at ON search_logs(created_at);
```

### Qdrant Collection

**Collection Name:** `product_embeddings`

**Configuration:**
- Vector size: 512 (CLIP embedding dimension)
- Distance metric: Cosine similarity
- Payload schema:
  ```json
  {
    "product_id": "string",
    "title": "string",
    "category": "string",
    "additional_metadata": "any"
  }
  ```

## Usage Examples

### PostgreSQL Operations

#### Create a Product

```python
from app.db import get_session, create_product

async with get_session() as session:
    product = await create_product(session, {
        "external_id": "prod_001",
        "title": "Red Sofa",
        "description": "Comfortable 3-seater sofa",
        "category": "furniture",
        "price": 599.99,
        "currency": "USD",
        "image_url": "https://example.com/sofa.jpg",
        "product_metadata": {"color": "red", "seats": 3}
    })
```

#### Query Products

```python
from app.db import get_session, get_products, get_product_by_external_id

async with get_session() as session:
    # Get all products (paginated)
    products = await get_products(session, skip=0, limit=20)
    
    # Get specific product
    product = await get_product_by_external_id(session, "prod_001")
```

#### Update Product

```python
from app.db import get_session, update_product

async with get_session() as session:
    updated = await update_product(session, product_id=1, {
        "price": 499.99,
        "product_metadata": {"color": "red", "seats": 3, "on_sale": True}
    })
```

### Qdrant Operations

#### Initialize Manager

```python
from app.db import QdrantManager

qdrant = QdrantManager()
await qdrant.create_collection(vector_size=512, distance="Cosine")
```

#### Add Product Embeddings

```python
# Generate embeddings using CLIP model
from app.models import CLIPModel

clip_model = CLIPModel()
image_embeddings = clip_model.encode_images([image1, image2, image3])

# Store in Qdrant
await qdrant.upsert_vectors(
    product_ids=["prod_001", "prod_002", "prod_003"],
    vectors=image_embeddings.tolist(),
    payloads=[
        {"title": "Red Sofa", "category": "furniture"},
        {"title": "Blue Chair", "category": "furniture"},
        {"title": "Wooden Table", "category": "furniture"}
    ]
)
```

#### Search Similar Products

```python
# Generate query embedding
query_embedding = clip_model.encode_image(query_image)

# Search in Qdrant
results = await qdrant.search_similar(
    query_vector=query_embedding.tolist(),
    top_k=10,
    score_threshold=0.7
)

# Process results
for result in results:
    print(f"Product: {result['id']}")
    print(f"Similarity: {result['score']:.2f}")
    print(f"Metadata: {result['payload']}")
```

## Complete Workflow Example

```python
import asyncio
from app.db import get_session, create_product, QdrantManager
from app.models import CLIPModel

async def add_product_with_embedding(
    product_data: dict,
    image_path: str
):
    """Add product to both PostgreSQL and Qdrant."""
    
    # 1. Save product metadata to PostgreSQL
    async with get_session() as session:
        product = await create_product(session, product_data)
        print(f"✅ Created product in PostgreSQL: {product.external_id}")
    
    # 2. Generate embedding using CLIP
    clip_model = CLIPModel()
    embedding = clip_model.encode_image(image_path)
    
    # 3. Store embedding in Qdrant
    qdrant = QdrantManager()
    await qdrant.upsert_vectors(
        product_ids=[product.external_id],
        vectors=[embedding.tolist()],
        payloads=[{
            "title": product.title,
            "category": product.category
        }]
    )
    print(f"✅ Stored embedding in Qdrant: {product.external_id}")
    
    return product

# Usage
asyncio.run(add_product_with_embedding(
    product_data={
        "external_id": "prod_001",
        "title": "Red Sofa",
        "category": "furniture",
        "price": 599.99,
        "currency": "USD",
        "image_url": "https://example.com/sofa.jpg"
    },
    image_path="./images/sofa.jpg"
))
```

## Maintenance

### Backup PostgreSQL

```bash
# Backup database
pg_dump -U postgres visual_search > backup.sql

# Restore database
psql -U postgres visual_search < backup.sql
```

### Backup Qdrant

```bash
# Qdrant automatically creates snapshots
# Access via API: http://localhost:6333/collections/product_embeddings/snapshots
```

### Monitor Database Status

```python
from app.db import get_session, QdrantManager
from sqlalchemy import text

async def check_database_status():
    """Check status of both databases."""
    
    # PostgreSQL
    async with get_session() as session:
        result = await session.execute(
            text("SELECT COUNT(*) FROM products")
        )
        product_count = result.scalar()
        print(f"PostgreSQL products: {product_count}")
    
    # Qdrant
    qdrant = QdrantManager()
    info = await qdrant.get_collection_info()
    print(f"Qdrant vectors: {info['vectors_count']}")
    print(f"Collection status: {info['status']}")
```

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -U postgres -h localhost -d visual_search

# View logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

### Qdrant Connection Issues

```bash
# Check if Qdrant is running
curl http://localhost:6333/collections

# View Docker logs (if using Docker)
docker logs qdrant

# Check collection status
curl http://localhost:6333/collections/product_embeddings
```

### Common Errors

**Error: "relation 'products' does not exist"**
- Solution: Run `python scripts/init_databases.py`

**Error: "Collection not found"**
- Solution: Run `python scripts/init_databases.py` or create collection manually

**Error: "asyncpg.exceptions.InvalidPasswordError"**
- Solution: Check PostgreSQL credentials in `.env` file

## Testing

Run database tests:

```bash
# Test PostgreSQL
pytest tests/test_database_modules.py::TestPostgreSQL -v

# Test Qdrant
pytest tests/test_database_modules.py::TestQdrant -v

# Test all
pytest tests/test_database_modules.py -v
```

## Performance Tips

1. **Use connection pooling** (already configured in postgres.py)
2. **Batch operations** when possible:
   ```python
   # Good: Batch insert
   await qdrant.upsert_vectors(product_ids, vectors, payloads)
   
   # Bad: Individual inserts in loop
   for pid, vec, payload in zip(product_ids, vectors, payloads):
       await qdrant.upsert_vectors([pid], [vec], [payload])
   ```

3. **Use appropriate indexes** (already configured)
4. **Set score_threshold** in searches to filter low-quality results
5. **Monitor query performance** using search_logs table

## Additional Resources

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)

