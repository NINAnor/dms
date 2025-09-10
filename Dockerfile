ARG TESTING_MODULE="dms.core.settings.test"

FROM ghcr.io/osgeo/gdal:ubuntu-full-3.10.1 AS base
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1
# install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.31 /uv /uvx /bin/
RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    apt-get update && apt-get install --no-install-recommends -yq \
    gettext curl build-essential python3-dev libldap2-dev libsasl2-dev ldap-utils git \
    pandoc lmodern texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra
WORKDIR /app
RUN curl -fsSL https://deb.nodesource.com/setup_22.x -o nodesource_setup.sh && bash nodesource_setup.sh
RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    apt-get update && apt-get install -y --fix-missing nodejs

FROM base AS app
COPY pyproject.toml uv.lock entrypoint.sh README.md .
COPY src/dms/manage.py src/dms/__init__.py src/dms/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

FROM scratch AS source
WORKDIR /app
COPY src src

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
ENV DATASETS_IPT_URLS=""
RUN uv run manage.py compilemessages -l no

FROM production AS tailwind
COPY --from=source /app .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync
ENV DJANGO_SETTINGS_MODULE="dms.core.settings.test"
ENV DATABASE_URL=""
ENV DATASETS_IPT_URLS=""
RUN uv run manage.py tailwind install
RUN uv run manage.py tailwind build

FROM app AS django
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra ldap --extra prod
COPY --from=production /app .
COPY --from=translation /app/src/dms/locale /app/src/dms/locale
COPY --from=source /app .
COPY --from=tailwind /app/src/dms/theme/static /app/src/dms/theme/static
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
