#!/bin/bash
set -euo pipefail

if [ -z "$APP_COMPONENT" ]; then
  echo "Please set APP_COMPONENT"
  exit 1
fi

echo "Waiting for services to become available..."

SERVICE_READINESS_TIMEOUT=60
./scripts/await_service.sh $SQL_HOST $SQL_PORT $SERVICE_READINESS_TIMEOUT
./scripts/await_service.sh $REDIS_HOST $REDIS_PORT $SERVICE_READINESS_TIMEOUT
./scripts/await_service.sh $MEILI_HOST $MEILI_PORT $SERVICE_READINESS_TIMEOUT


./scripts/ensure_sql.sh
./scripts/ensure_meili.sh
./scripts/migrate.sh up

if [ $APP_COMPONENT = "api" ]; then
  exec /app/scripts/run_api.sh
elif [ $APP_COMPONENT = "converter" ]; then
  exec /app/scripts/run_converter.sh
else
  echo "Unknown APP_COMPONENT: $APP_COMPONENT"
  exit 1
fi
