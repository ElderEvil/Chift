# Chift - Odoo Integration API

FastAPI-based application that synchronizes contacts and invoices from Odoo to a local PostgreSQL database with JWT authentication.

## Quick Links

- 🚢 [Deployment Guide](docs/DEPLOYMENT.md)

## Project Structure

```
chift/
├── app/                     # Main application package
│   ├── core/                # Core functionality (config, database, auth)
│   ├── models/              # SQLAlchemy ORM models
│   ├── repositories/        # Data access layer
│   ├── routers/             # FastAPI route handlers
│   ├── schemas/             # Pydantic models for validation
│   ├── services/            # Business logic layer
│   └── main.py              # FastAPI application entrypoint
├── alembic/                 # Database migrations
├── scripts/                 # Utility scripts
│   └── create_admin.py      # Create admin user
├── tests/                   # Test suite
├── docs/                    # Deployment guide
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker image definition
├── Makefile                 # Development commands
└── pyproject.toml           # Project dependencies and config
```

## Quick Start

```bash
# 1. Clone and install
git clone <repo-url>
cd chift
make install

# 2. Configure environment
cp .env.example .env
# Edit .env with your Odoo credentials

# 3. Run with Docker
make docker-up

# 4. Create admin user
uv run python -m scripts.create_admin

# 5. Test API
curl http://localhost:8000/health
```

## Development Commands

```bash
make dev              # Run development server
make migrate          # Run database migrations
make migrate-create   # Create new migration
make test             # Run tests
make lint             # Run linter
make format           # Format code
make clean            # Clean cache files
```

## API Endpoints

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/token` - Get JWT token
- `GET /api/v1/contacts` - List contacts
- `GET /api/v1/invoices` - List invoices
- `GET /health` - Health check

See the deployment guide for details.

## Technology Stack

- **Framework**: FastAPI 0.128+
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Auth**: JWT (python-jose)
- **Scheduler**: APScheduler
- **Linter**: Ruff

## License

MIT
