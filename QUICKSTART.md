# Quick Start Guide

Get up and running with the Visual Search Project in 5 minutes!

## Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Poetry (install with: `curl -sSL https://install.python-poetry.org | python3 -`)

## Quick Setup

### 1. Install Dependencies

```bash
make install
# or
poetry install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed (defaults work for local development).

### 3. Start Services

```bash
make dev-start
# or
docker-compose up -d
```

This starts PostgreSQL, Redis, and Qdrant.

### 4. Initialize Database

```bash
make init-db
# or
poetry run python scripts/load_sample_data.py
```

### 5. Start API Server

```bash
make api
# or
poetry run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. (Optional) Start Worker

In a new terminal:

```bash
make worker
# or
poetry run celery -A app.workers.celery_app worker --loglevel=info
```

## Test the API

### Open API Documentation

Visit: http://localhost:8000/docs

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

### Text Search

```bash
curl -X POST "http://localhost:8000/api/v1/search/text?query=modern+sofa&limit=5"
```

### Image Search

```bash
curl -X POST "http://localhost:8000/api/v1/search/image" \
  -F "image=@/path/to/your/image.jpg"
```

## Available Make Commands

```bash
make help              # Show all available commands
make install           # Install dependencies
make dev-start         # Start Docker services
make dev-stop          # Stop Docker services
make init-db           # Initialize database
make api               # Start API server
make worker            # Start Celery worker
make test              # Run tests
make test-cov          # Run tests with coverage
make lint              # Run linters
make format            # Format code
make clean             # Clean generated files
```

## Project Structure Overview

```
visual-search-project/
├── app/
│   ├── api/           # FastAPI endpoints
│   ├── models/        # CLIP model wrapper
│   ├── db/            # Database clients (PostgreSQL, Qdrant)
│   ├── workers/       # Celery background tasks
│   ├── schemas/       # Pydantic models
│   ├── utils/         # Helper functions
│   └── config.py      # Configuration
├── tests/             # Test suite
├── scripts/           # Utility scripts
└── docker-compose.yml # Development services
```

## Next Steps

1. **Add Products**: Use the `/api/v1/products` endpoint to add products
2. **Index Images**: Use Celery tasks to generate embeddings
3. **Search**: Use text or image search endpoints
4. **Customize**: Modify configuration in `.env` file

## Troubleshooting

### Services not starting?

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs postgres
docker-compose logs qdrant
docker-compose logs redis
```

### Database connection error?

```bash
# Restart services
make dev-stop
make dev-start

# Wait a few seconds for services to be ready
sleep 5

# Try again
make init-db
```

### Import errors?

```bash
# Ensure you're in the Poetry shell or use poetry run
poetry shell

# Or prefix commands with poetry run
poetry run python scripts/load_sample_data.py
```

## Development Workflow

1. Make changes to code
2. API auto-reloads (if using `--reload` flag)
3. Run tests: `make test`
4. Format code: `make format`
5. Check linting: `make lint`

## Production Deployment

See the main [README.md](README.md) for production deployment guidelines.

## Support

- 📖 Full documentation: [README.md](README.md)
- 🐛 Issues: Open an issue on GitHub
- 📚 API Docs: http://localhost:8000/docs (when running)

