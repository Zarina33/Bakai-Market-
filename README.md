# Visual Search Project

A production-ready visual search system for products using CLIP (Contrastive Language-Image Pre-training) model. This system enables semantic search across product catalogs using both text queries and image similarity.

## Features

- 🔍 **Text-to-Image Search**: Find products using natural language descriptions
- 🖼️ **Image-to-Image Search**: Find similar products by uploading an image
- ⚡ **Fast Vector Search**: Powered by Qdrant for efficient similarity search
- 📊 **Metadata Storage**: PostgreSQL for structured product data
- 🔄 **Background Processing**: Celery workers for async embedding generation
- 🚀 **REST API**: FastAPI-based API with automatic documentation
- 🐳 **Docker Support**: Complete docker-compose setup for development

## Architecture

```
┌─────────────┐
│   FastAPI   │ ← REST API endpoints
└──────┬──────┘
       │
       ├─────────────┬─────────────┐
       ↓             ↓             ↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│   CLIP   │  │PostgreSQL│  │  Qdrant  │
│  Model   │  │ (metadata)│  │ (vectors)│
└──────────┘  └──────────┘  └──────────┘
       ↑
       │
┌──────────────┐
│    Celery    │ ← Background workers
│   Workers    │
└──────────────┘
       ↑
       │
┌──────────────┐
│    Redis     │ ← Task queue & cache
└──────────────┘
```

## Requirements

- Python 3.9+
- Poetry (for dependency management)
- Docker & Docker Compose (for development environment)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd visual-search-project
```

### 2. Install Poetry

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Install Dependencies

```bash
poetry install
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```bash
# Example configuration
POSTGRES_PASSWORD=your_secure_password
CLIP_DEVICE=cuda  # or cpu if no GPU available
```

### 5. Start Infrastructure Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Qdrant (port 6333)

### 6. Initialize Database

```bash
poetry run python scripts/load_sample_data.py
```

## Usage

### Start the API Server

```bash
poetry run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

Interactive API documentation: `http://localhost:8000/docs`

### Start Celery Workers

In a separate terminal:

```bash
poetry run celery -A app.workers.celery_app worker --loglevel=info
```

### API Examples

#### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

#### Text Search

```bash
curl -X POST "http://localhost:8000/api/v1/search/text?query=red+car&limit=10"
```

#### Image Search

```bash
curl -X POST "http://localhost:8000/api/v1/search/image" \
  -F "image=@path/to/image.jpg" \
  -F "limit=10"
```

#### Create Product

```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "prod_001",
    "title": "Modern Sofa",
    "description": "Comfortable modern sofa",
    "category": "furniture",
    "price": 599.99,
    "currency": "USD",
    "image_url": "https://example.com/sofa.jpg"
  }'
```

#### Index Product (Background Task)

```python
from app.workers.tasks import index_product

# Trigger async indexing
task = index_product.delay(
    product_id="prod_001",
    image_url="https://example.com/image.jpg"
)

# Check task status
result = task.get()
```

## Development

### Run Tests

```bash
poetry run pytest
```

With coverage:

```bash
poetry run pytest --cov=app --cov-report=html
```

### Code Formatting

```bash
# Format code
poetry run black app tests

# Sort imports
poetry run isort app tests

# Lint
poetry run flake8 app tests
```

### Type Checking

```bash
poetry run mypy app
```

## Project Structure

```
visual-search-project/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration with pydantic-settings
│   ├── models/                # CLIP model wrapper
│   │   ├── __init__.py
│   │   └── clip_model.py
│   ├── db/                    # Database clients
│   │   ├── __init__.py
│   │   ├── postgres.py        # PostgreSQL client
│   │   └── qdrant.py          # Qdrant vector DB client
│   ├── api/                   # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app factory
│   │   └── routes/            # API endpoints
│   │       ├── __init__.py
│   │       ├── health.py
│   │       ├── search.py
│   │       └── products.py
│   ├── workers/               # Celery workers
│   │   ├── __init__.py
│   │   ├── celery_app.py      # Celery configuration
│   │   └── tasks.py           # Background tasks
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py
│   │   └── image_processing.py
│   └── schemas/               # Pydantic models
│       ├── __init__.py
│       ├── product.py
│       └── search.py
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_clip_model.py
│   └── test_api.py
├── scripts/                   # Utility scripts
│   ├── init.sql               # Database initialization
│   └── load_sample_data.py    # Load sample data
├── docker-compose.yml         # Docker services
├── .env.example               # Environment variables template
├── pyproject.toml             # Poetry dependencies
├── .gitignore
└── README.md
```

## Configuration

All configuration is managed through environment variables. See `.env.example` for available options.

Key settings:

- `CLIP_MODEL_NAME`: HuggingFace model name (default: `openai/clip-vit-base-patch32`)
- `CLIP_DEVICE`: Device for model inference (`cpu` or `cuda`)
- `QDRANT_COLLECTION_NAME`: Vector collection name
- `QDRANT_VECTOR_SIZE`: Embedding dimension (512 for default CLIP model)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

## Production Deployment

### Recommendations

1. **Use GPU for CLIP model**: Set `CLIP_DEVICE=cuda` for better performance
2. **Scale workers**: Run multiple Celery workers for parallel processing
3. **Enable authentication**: Add API authentication middleware
4. **Set up monitoring**: Use Prometheus + Grafana for metrics
5. **Configure CORS**: Restrict allowed origins in production
6. **Use connection pooling**: Configure PostgreSQL connection pool
7. **Enable caching**: Use Redis for caching frequent queries

### Docker Production Build

```bash
# Build production image
docker build -t visual-search-api:latest .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## Performance Considerations

- **Batch Processing**: Use `batch_index_products` task for bulk indexing
- **Vector Search**: Qdrant provides sub-millisecond search times
- **Caching**: Implement Redis caching for frequent queries
- **Model Loading**: CLIP model is loaded once and reused
- **Image Processing**: Images are resized to reduce memory usage

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres
```

### Qdrant Connection Issues

```bash
# Check Qdrant status
curl http://localhost:6333/collections

# View Qdrant logs
docker-compose logs qdrant
```

### CUDA/GPU Issues

If you encounter CUDA errors:

1. Verify GPU availability: `nvidia-smi`
2. Check PyTorch CUDA support: `python -c "import torch; print(torch.cuda.is_available())"`
3. Fallback to CPU: Set `CLIP_DEVICE=cpu` in `.env`

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/docs` endpoint

