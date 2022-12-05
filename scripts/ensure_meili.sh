#!/bin/bash
set -euo pipefail
echo "Creating Meilisearch index..."

# Ensure the meilisearch index exists
curl \
  -X POST "http://${MEILI_HOST}:${MEILI_PORT}/indexes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MEILI_KEY}" \
  --data-binary "{ \"uid\": \"levels\", \"primaryKey\": \"id\" }"

echo

# Configure filterable and sortable attributes
echo "Configuring index attributes..."
curl \
  -X PATCH "http://${MEILI_HOST}:${MEILI_PORT}/indexes/levels/settings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MEILI_KEY}" \
  --data-binary " { \
    \"filterableAttributes\": [ \
        \"custom_song_id\", \
        \"user_id\", \
        \"publicity\", \
        \"official_song_id\", \
        \"search_flags\", \
        \"feature_order\", \
        \"stars\", \
        \"length\", \
        \"two_player\", \
        \"difficulty\" \
    ], \
    \"sortableAttributes\": [ \
      \"downloads\", \
      \"likes\", \
      \"feature_order\" \
    ] \
  }"

echo
echo "Done!"
