#!/bin/bash
set -e

git switch main
git branch -d update-deps || true
git switch -c update-deps
git rebase main

uv audit -U || true

PROJECT_ROOT=$(pwd)

cd src/dms/frontend && pnpm audit --fix && pnpm install && cd $PROJECT_ROOT


. helpers.sh

docker compose --profile dev build --no-cache django-dev
docker compose --profile dev run --rm django-dev uv run pytest

git add pyproject.toml uv.lock src/dms/frontend/pnpm-lock.yaml src/dms/frontend/pnpm-workspace.yaml
git commit -m "dev: Update dependencies"
