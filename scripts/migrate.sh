#!/bin/bash
set -euo pipefail
DB_DSN="mysql://${SQL_USER}:${SQL_PASS}@tcp(${SQL_HOST}:${SQL_PORT})/${SQL_DB}"

# Support UP and DOWN migrations
if [ "$1" = "up" ]; then
    echo "Running UP migrations"
    go-migrate -path /app/database/migrations -database $DB_DSN up
elif [ "$1" = "down" ]; then
    echo "Running DOWN migrations"
    go-migrate -path /app/database/migrations -database $DB_DSN down
else
    echo "Usage: $0 [up|down]"
    exit 1
fi

echo "Done!"
