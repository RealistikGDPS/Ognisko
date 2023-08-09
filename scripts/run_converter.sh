#!/bin/bash
set -euo pipefail

echo "Starting converter..."
exec rgdps/utilities/gmdps_converter.py
