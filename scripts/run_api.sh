#!/bin/bash
set -euo pipefail

echo "Starting server..."
exec uvicorn ognisko.main:asgi_app \
    --host $OGNISKO_HTTP_HOST \
    --port $OGNISKO_HTTP_PORT \
    --reload
