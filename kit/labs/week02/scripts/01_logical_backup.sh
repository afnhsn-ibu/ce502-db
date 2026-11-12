#!/usr/bin/env bash
# CE 502 · Practice 2 · Part A · Step 1: logical backup with pg_dump (custom format), timed.
# Run: docker exec -u postgres ce502-postgres bash /kit/labs/week02/scripts/01_logical_backup.sh
set -euo pipefail
BACKUP_DIR="${BACKUP_DIR:-/backup}"

echo "== Database before the backup =="
psql -U postgres -d shop -c "SELECT count(*) AS orders, sum(amount) AS total_amount FROM orders"

echo "== Taking the backup: pg_dump -Fc shop > $BACKUP_DIR/shop.dump =="
START=$(date +%s%N)
pg_dump -U postgres -Fc -d shop -f "$BACKUP_DIR/shop.dump"
END=$(date +%s%N)
MS=$(( (END - START) / 1000000 ))
printf "Backup time: %d.%03d s\n" $((MS / 1000)) $((MS % 1000))
echo "Backup finished at: $(date '+%Y-%m-%d %H:%M:%S %Z')   <- write this down (it decides your RPO)"
ls -lh "$BACKUP_DIR/shop.dump" | awk '{print "Dump file size: " $5}'

echo
echo "== What is inside a custom-format dump? (first lines of its table of contents) =="
pg_restore -l "$BACKUP_DIR/shop.dump" | grep -v '^;' | head -12
