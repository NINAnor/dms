#!/bin/bash

set -o errexit
set -o pipefail

# Run commands to setup

uv run manage.py wait_for_database

if [[ -z "${WAIT_FOR_HTTP}" ]]
then
  echo "No HTTP service to wait for"
else
  uv run manage.py wait_for_http "$WAIT_FOR_HTTP"
fi

# Connecting to LDAPS may require custom CA certificates installed
if [[ -z "${LDAP_CA_FILE_PATH}" ]]
then
  echo "CA cert not installed"
else
  update-ca-certificates
fi


if [[ -z "${DJANGO_MIGRATE}" ]]
then
  echo "Skip migration and setup"
else
  uv run manage.py makemigrations
  uv run manage.py migrate
  uv run manage.py setup
  echo "Generate OpenAPI schema"
  uv run manage.py spectacular > schema.yml
fi

if [[ -z "${DJANGO_TAILWIND}" ]]
then
  echo "Skip tailwind"
else
  uv run manage.py tailwind install --no-input
fi

if [[ -z "${DJANGO_COLLECTSTATIC}" ]]
then
  echo "Skip collectstatic"
else
  uv run manage.py collectstatic --noinput
fi

exec "$@"
