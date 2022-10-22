#!/bin/bash
echo "Bootstrapping application..."
./scripts/ensure_db.sh
./scripts/migrate.sh up
./scripts/run.sh
