# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web Browser, Mobile App, API Consumer)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Health     │  │    Search    │  │   Products   │         │
│  │  Endpoints   │  │  Endpoints   │  │  Endpoints   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────┬────────────────────┬────────────────┬─────────────────┘
         │                    │                │
         ↓                    ↓                ↓
┌────────────────┐   ┌────────────────┐   ┌────────────────┐
│  CLIP Model    │   │  PostgreSQL    │   │    Qdrant      │
│   Wrapper      │   │   (Metadata)   │   │   (Vectors)    │
│                │   │                │   │                │
│ - encode_image │   │ - products     │   │ - embeddings   │
│ - encode_text  │   │ - search_logs  │   │ - similarity   │
│ - similarity   │   │                │   │   search       │
└────────────────┘   └────────────────┘   └────────────────┘
         ↑
         │
┌────────┴───────────────────────────────────────────────────────┐
│                    Celery Workers                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │    Index     │  │    Batch     │  │   Reindex    │        │
│  │   Product    │  │    Index     │  │     All      │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ↓
                    ┌────────────────┐
                    │     Redis      │
                    │ (Task Queue &  │
                    │  Result Store) │
                    └────────────────┘
```

## Component Details

### 1. API Layer (FastAPI)

**Purpose**: Handle HTTP requests and orchestrate operations

**Components**:
- `app/api/main.py`: Application factory and configuration
- `app/api/routes/health.py`: Health check endpoints
- `app/api/routes/search.py`: Search endpoints (text and image)
- `app/api/routes/products.py`: Product CRUD operations

**Responsibilities**:
- Request validation (Pydantic schemas)
- Response formatting
- Error handling
- CORS management
- API documentation (OpenAPI/Swagger)

### 2. CLIP Model Layer

**Purpose**: Encode images and text into embeddings

**Components**:
- `app/models/clip_model.py`: CLIP wrapper class

**Responsibilities**:
- Load and manage CLIP model
- Encode images to 512-dimensional vectors
- Encode text to 512-dimensional vectors
- Compute cosine similarity
- Handle batch processing
- Manage GPU/CPU device selection

**Model**: `openai/clip-vit-base-patch32` (configurable)

### 3. Database Layer

#### PostgreSQL (Metadata Storage)

**Purpose**: Store structured product data

**Components**:
- `app/db/postgres.py`: PostgreSQL client

**Schema**:
```sql
products:
  - id (serial)
  - external_id (varchar, unique)
  - title (varchar)
  - description (text)
  - category (varchar)
  - price (decimal)
  - currency (varchar)
  - image_url (text)
  - metadata (jsonb)
  - created_at (timestamp)
  - updated_at (timestamp)

search_logs:
  - id (serial)
  - query_type (varchar)
  - query_text (text)
  - query_image_url (text)
  - results_count (integer)
  - execution_time_ms (integer)
  - user_id (varchar)
  - session_id (varchar)
  - created_at (timestamp)
```

#### Qdrant (Vector Storage)

**Purpose**: Store and search embeddings

**Components**:
- `app/db/qdrant.py`: Qdrant client

**Collection**:
- Name: `product_embeddings`
- Vector size: 512
- Distance metric: Cosine
- Payload: `{product_id, image_url, ...}`

### 4. Worker Layer (Celery)

**Purpose**: Process background tasks asynchronously

**Components**:
- `app/workers/celery_app.py`: Celery configuration
- `app/workers/tasks.py`: Task definitions

**Tasks**:
1. `index_product`: Index single product image
2. `batch_index_products`: Index multiple products
3. `reindex_all_products`: Reindex entire catalog

**Features**:
- Retry logic with exponential backoff
- Task tracking
- Result storage
- Time limits

### 5. Configuration Layer

**Purpose**: Centralized configuration management

**Components**:
- `app/config.py`: Settings class with validation
- `.env`: Environment variables

**Features**:
- Type-safe configuration
- Environment variable validation
- Computed properties
- Field validators
- Default values

### 6. Utilities Layer

**Purpose**: Shared helper functions

**Components**:
- `app/utils/image_processing.py`: Image utilities

**Functions**:
- Download images with retry
- Process and resize images
- Validate image formats
- Extract image dimensions

## Data Flow

### Text Search Flow

```
1. Client sends text query
   ↓
2. FastAPI receives request
   ↓
3. CLIP encodes text to embedding
   ↓
4. Qdrant searches for similar vectors
   ↓
5. PostgreSQL fetches product metadata
   ↓
6. FastAPI returns results to client
```

### Image Search Flow

```
1. Client uploads image
   ↓
2. FastAPI receives image file
   ↓
3. Image is processed (resize, convert)
   ↓
4. CLIP encodes image to embedding
   ↓
5. Qdrant searches for similar vectors
   ↓
6. PostgreSQL fetches product metadata
   ↓
7. FastAPI returns results to client
```

### Product Indexing Flow

```
1. Product created via API
   ↓
2. Product saved to PostgreSQL
   ↓
3. Celery task triggered
   ↓
4. Worker downloads product image
   ↓
5. CLIP generates embedding
   ↓
6. Embedding stored in Qdrant
   ↓
7. Task result returned
```

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  PostgreSQL  │  │    Redis     │  │   Qdrant     │ │
│  │   :5432      │  │    :6379     │  │   :6333      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
         ↑                  ↑                  ↑
         │                  │                  │
┌────────┴──────────────────┴──────────────────┴─────────┐
│                    Host Machine                         │
│  ┌──────────────┐                  ┌──────────────┐   │
│  │  FastAPI     │                  │    Celery    │   │
│  │  :8000       │                  │   Worker     │   │
│  └──────────────┘                  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Production Environment (Recommended)

```
                    ┌──────────────┐
                    │ Load Balancer│
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
    ┌──────────┐     ┌──────────┐     ┌──────────┐
    │ FastAPI  │     │ FastAPI  │     │ FastAPI  │
    │ Instance │     │ Instance │     │ Instance │
    └─────┬────┘     └─────┬────┘     └─────┬────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
    ┌──────────┐     ┌──────────┐     ┌──────────┐
    │PostgreSQL│     │  Qdrant  │     │  Redis   │
    │ (Primary)│     │ Cluster  │     │ Cluster  │
    └─────┬────┘     └──────────┘     └─────┬────┘
          │                                   │
    ┌─────┴────┐                             │
    │PostgreSQL│                             │
    │(Replica) │                             │
    └──────────┘                             │
                                             │
          ┌──────────────────────────────────┘
          ↓
    ┌──────────┐     ┌──────────┐     ┌──────────┐
    │  Celery  │     │  Celery  │     │  Celery  │
    │ Worker 1 │     │ Worker 2 │     │ Worker 3 │
    └──────────┘     └──────────┘     └──────────┘
```

## Scalability Considerations

### Horizontal Scaling

1. **API Layer**: Multiple FastAPI instances behind load balancer
2. **Workers**: Multiple Celery workers for parallel processing
3. **Databases**: 
   - PostgreSQL: Primary-replica setup
   - Qdrant: Distributed cluster
   - Redis: Redis Cluster or Sentinel

### Vertical Scaling

1. **GPU**: Use CUDA for faster CLIP inference
2. **Memory**: Increase for larger batch sizes
3. **CPU**: More cores for concurrent requests

### Optimization Strategies

1. **Caching**:
   - Cache frequent queries in Redis
   - Cache CLIP embeddings
   - HTTP caching headers

2. **Batch Processing**:
   - Batch CLIP inference
   - Batch database operations
   - Batch vector insertions

3. **Connection Pooling**:
   - PostgreSQL connection pool
   - Redis connection pool
   - HTTP connection pooling

4. **Async Operations**:
   - FastAPI async endpoints
   - Async database queries
   - Background task processing

## Security Architecture

### Authentication & Authorization

```
Client → API Gateway → JWT Validation → FastAPI
                           ↓
                    User Permissions Check
                           ↓
                    Database/Service Access
```

### Data Protection

1. **In Transit**: HTTPS/TLS for all connections
2. **At Rest**: Encrypted database storage
3. **Secrets**: Environment variables, not in code
4. **Input Validation**: Pydantic schemas

### Network Security

1. **Firewall**: Restrict database ports
2. **VPC**: Isolated network for services
3. **CORS**: Configured allowed origins
4. **Rate Limiting**: Prevent abuse

## Monitoring & Observability

### Metrics to Track

1. **API Metrics**:
   - Request rate
   - Response time
   - Error rate
   - Status codes

2. **Search Metrics**:
   - Search latency
   - Result quality
   - Cache hit rate

3. **Worker Metrics**:
   - Task queue length
   - Task processing time
   - Task success/failure rate

4. **Database Metrics**:
   - Query performance
   - Connection pool usage
   - Storage usage

### Logging Strategy

1. **Structured Logging**: JSON format
2. **Log Levels**: DEBUG, INFO, WARNING, ERROR
3. **Correlation IDs**: Track requests across services
4. **Centralized Logs**: ELK stack or similar

### Health Checks

1. **Liveness**: Is the service running?
2. **Readiness**: Can the service handle requests?
3. **Dependencies**: Are databases accessible?

## Technology Choices & Rationale

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Web Framework | FastAPI | Fast, modern, auto-docs, async support |
| ML Model | CLIP | State-of-art vision-language model |
| Vector DB | Qdrant | Fast, easy to use, good Python support |
| Relational DB | PostgreSQL | Robust, JSONB support, mature |
| Task Queue | Celery + Redis | Industry standard, reliable |
| Validation | Pydantic | Type-safe, great FastAPI integration |
| Dependency Mgmt | Poetry | Modern, deterministic builds |
| Containerization | Docker | Standard, reproducible environments |

---

**Last Updated**: November 5, 2025

