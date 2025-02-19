#!/bin/bash

BASE_CMD="docker compose --profile"

export HOSTNAME

alias dpcli_dev="$BASE_CMD dev"
alias dpcli_prod="$BASE_CMD prod"

alias djcli_dev="dpcli_dev exec -it django-dev uv run manage.py"
alias djcli_prod="dpcli_prod exec -it django uv run manage.py"
