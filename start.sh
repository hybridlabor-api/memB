#!/usr/bin/env bash
# start.sh for memB Semantic Graph backend

set -e

# Change to the directory of this script
cd "$(dirname "$0")"

# Export PYTHONPATH so the src module can be resolved
export PYTHONPATH="${PYTHONPATH}:${PWD}"

echo "Starting memB backend on port 8088..."
exec uvicorn src.backend.server:app --port 8088
