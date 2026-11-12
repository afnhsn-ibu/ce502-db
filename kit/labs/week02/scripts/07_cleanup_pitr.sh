#!/usr/bin/env bash
# CE 502 · Practice 2 · Part B · Clean up: stop the recovered server and remove its files.
# Run: docker exec -u postgres ce502-postgres bash /kit/labs/week02/scripts/07_cleanup_pitr.sh
set -euo pipefail
BACKUP_DIR="${BACKUP_DIR:-/backup}"
pg_ctl -D "$BACKUP_DIR/pitr" stop -m fast 2>/dev/null || echo "The recovered server was not running."
rm -rf "$BACKUP_DIR/pitr" "$BACKUP_DIR/pitr.log"
echo "Removed $BACKUP_DIR/pitr. The base backup in $BACKUP_DIR/base and the WAL archive are kept."
echo "To start Practice 2 again from the beginning: run sql/00_create_shop.sql."
