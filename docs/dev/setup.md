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

2. **Configure required environment variables** in `.env`: if using an external bucket make sure to fill the correct values.

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
- **rustfs**: S3-compatible object storage (dev only)
- **tusd**: S3 upload service
- **frontend**: Frontend development server for high interaction pages (dev only)
- **titiler**: A TMS service to provide previews of COG files
- **fastdoc**: pandoc converter API (for generating nice documents in multi formats, pdf generation)

## Development mode
In development mode it's especially important to set correctly the rustfs endpoint.
The address of the bucket must be resolvable both by the browser and the docker containers, so:

- if you are using an external bucket, set the `AWS` variables ignoring rustfs
- if you have `sudo`, edit `/etc/hosts` adding `rustfs.local`
- if you don't have `sudo`, use your computer hostname (execute `hostname` in any shell)

This will ensure that your browser works and docker will fallback to host for domain resolution (localhost instead would be resolved in the running container)

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
