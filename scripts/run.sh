#!/bin/bash
set -euo pipefail

echo "Starting server..."
exec uvicorn rgdps.main:asgi_app \
    --host $HTTP_HOST \
    --port $HTTP_PORT
