#!/bin/bash
set -euo pipefail
echo "Creating meilisearch index levels..."

curl \
  -X POST "http://${MEILI_HOST}:${MEILI_PORT}/indexes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MEILI_KEY}" \
  --data-binary "{ \"uid\": \"levels\", \"primaryKey\": \"id\" }"

echo
echo "Done!"
