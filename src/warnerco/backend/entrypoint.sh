#!/bin/sh
# WARNERCO Schematica container entrypoint.
#
# The Azure Files volume mounts at /app/data and SHADOWS anything baked into that
# path in the image. The knowledge graph (data/graph/knowledge.db) and the seed
# schematics are baked at build time, so on a fresh share they would be invisible
# and the query_graph LangGraph node would return empty.
#
# Fix: the image carries the seed under /app/seed (never mounted). On first boot,
# if a target subdir is missing on the mounted share, copy it across. Idempotent -
# subsequent boots find the data already there and skip the copy, so runtime writes
# (scratchpad, episodic) are preserved across restarts.
set -e

SEED_DIR="/app/seed"
DATA_DIR="/app/data"

seed_if_absent() {
    # $1 = subdirectory name under data/ (e.g. "graph", "schematics")
    if [ -d "$SEED_DIR/$1" ] && [ ! -e "$DATA_DIR/$1" ]; then
        echo "[entrypoint] seeding $1 onto persistent volume"
        cp -r "$SEED_DIR/$1" "$DATA_DIR/$1"
    fi
}

mkdir -p "$DATA_DIR"
# Read-mostly seed data that the app expects under data/. Scratchpad and episodic
# dirs are created by the app on demand, so they are intentionally not seeded.
seed_if_absent graph
seed_if_absent schematics

# Hand off to the real server process (PID 1 semantics preserved via exec).
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 \
    --proxy-headers --forwarded-allow-ips '*'
