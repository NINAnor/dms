#!/bin/sh
# Starts the RustFS server, then provisions the default bucket and its
# public-read policy using the `rc` CLI baked into this image. Equivalent
# in spirit to the old `mkdir -p /data/django && minio server ...` one-liner,
# with bucket + policy provisioning chained on.
set -u

DATA_DIR="${RUSTFS_DATA_DIR:-/data}"
BUCKET="${RUSTFS_DEFAULT_BUCKET:-django}"
ENDPOINT="${RUSTFS_LOCAL_ENDPOINT:-http://127.0.0.1:9090}"
ACCESS_KEY="${RUSTFS_ACCESS_KEY:?RUSTFS_ACCESS_KEY must be set}"
SECRET_KEY="${RUSTFS_SECRET_KEY:?RUSTFS_SECRET_KEY must be set}"

mkdir -p "$DATA_DIR"

rustfs server "$DATA_DIR" --address ":9090" --console-address ":9091" &
SERVER_PID=$!

trap 'kill "$SERVER_PID" 2>/dev/null' TERM INT

rc alias set local "$ENDPOINT" "$ACCESS_KEY" "$SECRET_KEY" >/dev/null 2>&1

# Retry bucket creation until the server is actually accepting requests.
# Provisioning is a hard requirement, not best-effort: if the server never
# comes up we fail the container rather than run unprovisioned.
i=0
until rc mb "local/$BUCKET" --ignore-existing >/dev/null 2>&1; do
  i=$((i + 1))
  if [ "$i" -ge 30 ]; then
    echo "rustfs: could not create bucket '$BUCKET' after 30s" >&2
    kill "$SERVER_PID" 2>/dev/null
    exit 1
  fi
  sleep 1
done

if ! rc anonymous set download "local/$BUCKET"; then
  echo "rustfs: could not set public-read policy on bucket '$BUCKET'" >&2
  kill "$SERVER_PID" 2>/dev/null
  exit 1
fi

# Allow direct-from-browser uploads (Uppy's AwsS3 plugin with the signRequest
# strategy PUTs straight to this bucket from the frontend's origin), which
# requires the bucket to answer CORS preflights.
CORS_FILE="$(mktemp)"
cat >"$CORS_FILE" <<'EOF'
{
  "rules": [
    {
      "allowedOrigins": ["*"],
      "allowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
      "allowedHeaders": ["*"],
      "exposeHeaders": ["ETag", "Location"],
      "maxAgeSeconds": 3000
    }
  ]
}
EOF
if ! rc bucket cors set "local/$BUCKET" "$CORS_FILE" >/dev/null 2>&1; then
  echo "rustfs: could not set CORS rules on bucket '$BUCKET'" >&2
  kill "$SERVER_PID" 2>/dev/null
  exit 1
fi
rm -f "$CORS_FILE"

wait "$SERVER_PID"
