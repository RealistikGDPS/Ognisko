#!/bin/bash
set -euo pipefail

echo "Waiting for SQL to become available..."

./scripts/await_service.sh $SQL_HOST $SQL_PORT $SERVICE_READINESS_TIMEOUT

./scripts/ensure_sql.sh
./scripts/ensure_meili.sh
./scripts/migrate.sh up
exec ./scripts/run.sh
