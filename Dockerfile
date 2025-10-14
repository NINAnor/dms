ARG TESTING_MODULE="dms.core.settings.test"

FROM ghcr.io/osgeo/gdal:ubuntu-full-3.11.2 AS base
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
# install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.31 /uv /uvx /bin/
RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    apt-get update && apt-get install --no-install-recommends -yq \
    gettext curl build-essential python3-dev libldap2-dev libsasl2-dev ldap-utils git
WORKDIR /app
RUN curl -fsSL https://deb.nodesource.com/setup_22.x -o nodesource_setup.sh && bash nodesource_setup.sh
RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    apt-get update && apt-get install -y --fix-missing nodejs

FROM base AS app
COPY pyproject.toml uv.lock entrypoint.sh README.md ./
COPY src/dms/manage.py src/dms/__init__.py src/dms/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

FROM scratch AS source
WORKDIR /app
COPY src src


FROM node:22-slim AS frontend-base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app
COPY src/dms/frontend/package.json src/dms/frontend/pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile


FROM frontend-base AS frontend
COPY src/dms/frontend/src src
COPY src/dms/frontend/vite.config.ts src/dms/frontend/eslint.config.js src/dms/frontend/*.json src/dms/frontend/.prettierignore ./

FROM frontend AS frontend-prod
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm run build

FROM app AS production
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra prod
ENV PATH="/app/.venv/bin:$PATH"

FROM production AS translation
COPY --from=source /app .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync
ENV DJANGO_SETTINGS_MODULE="dms.core.settings.test"
ENV DATABASE_URL=""
RUN uv run manage.py compilemessages -l no

FROM production AS tailwind
COPY --from=source /app .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync
ENV DJANGO_SETTINGS_MODULE="dms.core.settings.test"
ENV DATABASE_URL=""
RUN uv run manage.py tailwind install
RUN uv run manage.py tailwind build

FROM app AS django
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra ldap --extra prod
COPY --from=production /app .
COPY --from=translation /app/src/dms/locale /app/src/dms/locale
COPY --from=source /app .
COPY --from=tailwind /app/src/dms/theme/static /app/src/dms/theme/static
COPY --from=frontend-prod /app/static /app/src/frontend/static
RUN mkdir media
ENTRYPOINT ["./entrypoint.sh"]

FROM app AS dev
COPY --from=production /app .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --all-extras
COPY --from=django /app/src src
COPY --from=translation /app/src/dms/locale /app/src/dms/locale
COPY --from=django /app/entrypoint.sh .
ENTRYPOINT ["./entrypoint.sh"]
