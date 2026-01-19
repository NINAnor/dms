# Project Structure

This page documents the high-level structure of the repository and where to find key components.

## Overview

Top-level layout:

- `mkdocs.yml`, `README.md`, `pyproject.toml` — repository metadata and build config.
- `docs/` — site documentation (this page).
- `src/dms/` — main Django project package containing apps for the DMS.
- `volumes/` — local volume data used for development (e.g. minio data stores).

## `src/dms/`

This is the primary application code. Important subpackages:

- `core/` — project wiring: `apps.py`, `wsgi.py`, `urls.py`, common helpers, storages, and tasks.
- `datasets/` — dataset models, admin, views, APIs, tables, and project-specific rules.
- `projects/` — project-scoped models, admin, forms and views.
- `services/` — service-related apps and endpoints.
- `frontend/` — Django-side integration for the modern frontend (views to serve the SPA, build config in `frontend/`).
- `theme/` — UI theme layer, templates and static sources for shared look-and-feel.
- `uploads/`, `users/` — smaller apps handling file uploads, user extensions.

Each app typically contains `models.py`, `admin.py`, `views.py`, `urls.py`, `templates/`, and `migrations/`.

## Frontend

There is a JS/TS-based frontend under `src/dms/frontend/`. Look for `package.json`, `tsconfig.*` and `vite.config.ts` for the frontend build and dev server configuration.

## Static assets and templates

- `src/dms/static/` — compiled or collected static files served by Django.
- `src/dms/templates/` — Django templates used by server-rendered pages.

## Fixtures, management and tests

- `fixtures/` — example data used for development or tests.
- `management/` — custom Django management commands.
- `tests/` — unit and integration tests associated with apps (look inside each app for its `tests/` folder).

## Development run

Common developer entrypoints:

- `src/dms/manage.py` — runserver, migrations, shell, etc.
- Docker-compose scripts in `docker-compose.yml` and `Dockerfile` are used for containerized development and services

## Where to look for configuration

- App settings and environment-specific config live under `src/dms/settings/`.
