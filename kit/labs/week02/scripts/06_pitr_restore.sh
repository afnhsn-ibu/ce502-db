#!/usr/bin/env bash
# CE 502 · Practice 2 · Part B · Step 3: point-in-time recovery into a SECOND server (port 5434).
# The damaged server keeps running, so you can compare both. This is the "restore somewhere new
# first, check it, then switch" rule from Lesson 2-3.
# Run: docker exec -u postgres ce502-postgres bash /kit/labs/week02/scripts/06_pitr_restore.sh "2026-10-26 14:30:05 CET"
set -euo pipefail
TARGET="${1:?Give the recovery target time printed by 05_work_then_disaster.sql (in quotes)}"
BACKUP_DIR="${BACKUP_DIR:-/backup}"
ARCHIVE_DIR="${ARCHIVE_DIR:-/archive}"
PITR_DIR="$BACKUP_DIR/pitr"
PITR_PORT="${PITR_PORT:-5434}"

echo "== 1. Copy the base backup into a new data directory: $PITR_DIR =="
pg_ctl -D "$PITR_DIR" stop -m fast >/dev/null 2>&1 || true
rm -rf "$PITR_DIR"
cp -a "$BACKUP_DIR/base" "$PITR_DIR"
chmod 700 "$PITR_DIR"

echo "== 2. Recovery settings (added to postgresql.auto.conf) =="
cat >> "$PITR_DIR/postgresql.auto.conf" <<CONF
# --- CE 502 point-in-time recovery ---
restore_command = 'cp $ARCHIVE_DIR/%f %p'
recovery_target_time = '$TARGET'
recovery_target_action = 'promote'
port = $PITR_PORT
archive_mode = off
CONF
tail -6 "$PITR_DIR/postgresql.auto.conf"
touch "$PITR_DIR/recovery.signal"      # tells PostgreSQL: start in recovery mode

echo "== 3. Start the second server and let it replay the archived WAL =="
START=$(date +%s%N)
pg_ctl -D "$PITR_DIR" -l "$BACKUP_DIR/pitr.log" -o "-c archive_mode=off" -w -t 120 start >/dev/null
until psql -U postgres -p "$PITR_PORT" -d postgres -tAc "SELECT NOT pg_is_in_recovery()" 2>/dev/null | grep -q t; do sleep 1; done
END=$(date +%s%N)
MS=$(( (END - START) / 1000000 ))
printf "Recovery time (start + replay): %d.%03d s\n" $((MS / 1000)) $((MS % 1000))

echo
echo "== 4. Recovery messages from the server log =="
grep -E "starting point-in-time recovery|restored log file|recovery stopping|archive recovery complete|selected new timeline" \
     "$BACKUP_DIR/pitr.log" | sed -E 's/^[0-9-]+ [0-9:.]+ [A-Z+0-9]+ //' | tail -8

echo
echo "== 5. Is the table back? =="
psql -U postgres -p "$PITR_PORT" -d shop -c \
  "SELECT count(*) AS orders, max(id) AS newest_order, sum(amount) AS total_amount FROM orders"
echo "Compare with the live server, where orders no longer exists:"
psql -U postgres -d shop -tAc "SELECT to_regclass('orders') IS NOT NULL AS orders_exists_on_live_server"
echo
echo "When you have finished: bash /kit/labs/week02/scripts/07_cleanup_pitr.sh"
