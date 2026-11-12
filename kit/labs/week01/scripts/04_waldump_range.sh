#!/usr/bin/env bash
# CE 502 · Practice 1 · Part B · Step 4b: show the log records between two LSNs.
# Usage (from your laptop):
#   docker exec -u postgres ce502-postgres bash /kit/labs/week01/scripts/04_waldump_range.sh <start_lsn> <end_lsn>
set -euo pipefail
START="${1:?Give the start LSN (a) printed by 04_checkpoint_fpw.sql}"
END="${2:?Give the end LSN (c) printed by 04_checkpoint_fpw.sql}"
PGDATA="${PGDATA:-/var/lib/postgresql/data}"

echo "== Log records from $START to $END =="
pg_waldump -p "$PGDATA/pg_wal" -s "$START" -e "$END" 2>/dev/null || true
echo
echo "Compare the two UPDATE records (Heap). The first ends with 'FPW' and its total length"
echo "(the number after the slash in 'len (rec/tot)') is about 8 kB: it carries a full-page image."
echo "The second has no FPW and is under 100 bytes: it carries only the change."
