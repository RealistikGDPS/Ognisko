#!/bin/bash
set -euo pipefail

echo "Starting converter..."
exec ognisko/components/gmdps_converter.py
