#!/bin/bash
set -euo pipefail
echo "Creating database ${SQL_DB}..."
mysql \
    --host=${SQL_HOST} \
    --port=${SQL_PORT} \
    --user=root \
    --password=${SQL_PASS} \
    --execute="CREATE DATABASE IF NOT EXISTS ${SQL_DB};"

if [ $? -ne 0 ]; then
    echo "Failed to create database ${SQL_DB}"
    exit 1
fi

echo "Done!"
