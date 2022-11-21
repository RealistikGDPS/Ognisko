#!/bin/bash
set -euo pipefail
echo "Bootstrapping application..."
./scripts/ensure_sql.sh
./scripts/ensure_meili.sh
./scripts/migrate.sh up
exec ./scripts/run.sh
