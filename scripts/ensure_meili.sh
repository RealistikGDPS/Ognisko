#!/bin/bash
set -euo pipefail
echo "Creating Meilisearch indices..."

# Ensure the meilisearch indices exist
curl \
  -X POST "http://${MEILI_HOST}:${MEILI_PORT}/indexes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MEILI_KEY}" \
  --data-binary "{ \"uid\": \"levels\", \"primaryKey\": \"id\" }"

curl \
  -X POST "http://${MEILI_HOST}:${MEILI_PORT}/indexes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MEILI_KEY}" \
  --data-binary "{ \"uid\": \"users\", \"primaryKey\": \"id\" }"

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
        \"epic\", \
        \"magic\", \
        \"awarded\", \
        \"feature_order\", \
        \"stars\", \
        \"length\", \
        \"two_player\", \
        \"difficulty\", \
        \"id\" \
    ], \
    \"sortableAttributes\": [ \
      \"downloads\", \
      \"likes\", \
      \"feature_order\", \
      \"upload_ts\" \
    ] \
  }"

curl \
  -X PATCH "http://${MEILI_HOST}:${MEILI_PORT}/indexes/users/settings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MEILI_KEY}" \
  --data-binary " { \
    \"filterableAttributes\": [ \
        \"is_public\"
    ]
  }"

echo
echo "Done!"
