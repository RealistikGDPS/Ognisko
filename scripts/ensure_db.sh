#!/bin/bash
echo "Creating database ${SQL_DB}..."
mysql \
    --host=${SQL_HOST} \
    --port=${SQL_PORT} \
    --user=${SQL_USER} \
    --password=${SQL_PASS} \
    --execute="CREATE DATABASE IF NOT EXISTS ${SQL_DB};"

echo "Done!"
