#!/usr/bin/env bash
set -e

export SCRIPT_PATH=/docker-entrypoint-initdb.d/
export PGPASSWORD=test
psql -f "$SCRIPT_PATH/scripts/db.sql"