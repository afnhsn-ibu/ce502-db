#!/usr/bin/env bash
# CE 502 · Practice 1 · Part B · Step 4a: read your own transaction from the binary log.
# Usage (from your laptop):
#   docker exec -u postgres ce502-postgres bash /kit/labs/week01/scripts/03_waldump.sh <wal_file> <txid>
set -euo pipefail
WAL_FILE="${1:?Give the wal_file printed by 02_my_transaction.sql}"
TXID="${2:?Give the my_txid printed by 02_my_transaction.sql}"
PGDATA="${PGDATA:-/var/lib/postgresql/data}"

# Make sure the COMMIT record has reached the file we read (it normally has).
psql -U postgres -d lab -qtAc "SELECT pg_current_wal_lsn()" >/dev/null

echo "== Log records written by transaction $TXID (pg_waldump -x $TXID) =="
# pg_waldump stops with an error at the unfinished end of the current file; that is normal.
pg_waldump -x "$TXID" "$PGDATA/pg_wal/$WAL_FILE" 2>/dev/null || true
echo
echo "Each line is one log record. Find: rmgr (which part of the DBMS wrote it), tx (your transaction),"
echo "lsn (its address in the log), prev (address of the record before it), desc (what changed),"
echo "and the last record: Transaction ... COMMIT <time>."
