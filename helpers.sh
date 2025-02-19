#!/bin/bash

BASE_CMD="docker compose --profile"

export HOSTNAME

alias dpcli_dev="$BASE_CMD dev"
alias dpcli_maps="$BASE_CMD maps"
alias dpcli_prod="$BASE_CMD prod"

alias djcli_dev="dpcli_dev exec -it django-dev python manage.py"
alias djcli_maps="dpcli_maps exec -it django-dev python manage.py"
alias djcli_prod="dpcli_prod exec -it django python manage.py"
