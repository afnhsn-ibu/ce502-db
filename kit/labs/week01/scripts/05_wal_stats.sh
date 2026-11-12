#!/usr/bin/env bash
# CE 502 · Practice 1 · Extension (optional): which parts of the DBMS write the most log?
# Usage: docker exec -u postgres ce502-postgres bash /kit/labs/week01/scripts/05_wal_stats.sh <wal_file>
set -euo pipefail
WAL_FILE="${1:?Give a WAL file name, e.g. from SELECT pg_walfile_name(pg_current_wal_lsn());}"
PGDATA="${PGDATA:-/var/lib/postgresql/data}"
pg_waldump --stats "$PGDATA/pg_wal/$WAL_FILE" 2>/dev/null || true
