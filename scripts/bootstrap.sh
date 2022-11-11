#!/bin/bash
echo "Bootstrapping application..."
./scripts/ensure_meili.sh
./scripts/ensure_sql.sh
./scripts/migrate.sh up
./scripts/run.sh
