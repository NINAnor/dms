#!/bin/bash

BASE_CMD="docker compose --profile"

export HOSTNAME

alias dpcli_dev="$BASE_CMD dev"
alias dpcli_prod="$BASE_CMD prod"

alias djcli_dev="dpcli_dev exec -it django-dev uv run manage.py"
alias djcli_prod="dpcli_prod exec -it django uv run manage.py"

alias dpcli_test="docker compose --profile dev exec -it django-dev uv run pytest"

[ ! -f oidc.key ] && openssl genrsa -out oidc.key 4096
export OIDC_RSA_PRIVATE_KEY=$(cat oidc.key)

if docker info 2>/dev/null | grep -q "rootless"; then
    export DOCKER_SOCK=/run/user/$(id -u)/docker.sock
else
    export DOCKER_SOCK=/var/run/docker.sock
fi

export HOSTNAME=$(hostname)
