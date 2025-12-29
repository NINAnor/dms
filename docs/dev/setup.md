# Setup

## Requirements
- GNU/Linux
- Docker
- uv
- pixi (optional)
- git


## Quick Start

1. **Copy environment variables:**

```bash
cp .env.example .env
```

2. **Configure required environment variables** in `.env`: Only `POSTGRES_PASSWORD` and `DJANGO_SECRET_KEY` are required. For these values you can choose your own

3. **Start the application:**

```bash
# For development
docker compose --profile dev up -d --build

# For production
docker compose --profile prod up -d --build
```

**NOTE**: A helper function provides aliases for running commands with the correct profile:
```bash
source ./helper.sh
```

Available aliases:
- `dpcli_dev`: `docker compose --profile dev`
- `dpcli_prod`: `docker compose --profile prod`
- `djcli_dev`: `docker compose --profile dev exec -it django-dev uv run manage.py` - execute a `django` command in the container (development)
- `djcli_prod`: `docker compose --profile prod exec -it django uv run manage.py` - execute a `django` command in the container (prod)

A super user is created on first run with the following credentials:
- Username: `admin`
- Password: `admin`


## Docker Compose Services

### Service architecture:
- **django/django-dev**: Main Django application server
- **queue/queue-dev**: Background task processor (Procrastinate worker)
- **tailwind**: CSS compilation service (dev only)
- **postgres**: PostGIS-enabled PostgreSQL database
- **nginx**: Nginx for static file serving (prod only)
- **traefik**: Reverse proxy
- **minio**: S3-compatible object storage (dev only)
- **tusd**: S3 upload service
- **frontend**: Frontend development server for high interaction pages (dev only)

## Development mode

**Start development environment:**

```bash
dpcli_dev up -d --build
```

**Development features:**

- Hot reload for code changes
- Tailwind CSS compilation with live updates
- Debug mode enabled

## Production mode

**Start production environment:**

```bash
dpcli_prod up -d --build
```

**Production features:**

- Gunicorn WSGI server
- Static file serving
- Production-optimized settings
- No development tools

**Important for production:**

- Set a secure `DJANGO_SECRET_KEY`
- Configure proper `DJANGO_ALLOWED_HOSTS`
