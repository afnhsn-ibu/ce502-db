#!/usr/bin/env bash
# CE 502 · Practice 2 · Part B · Step 1: check WAL archiving, then take a physical base backup.
# Run: docker exec -u postgres ce502-postgres bash /kit/labs/week02/scripts/04_base_backup.sh
set -euo pipefail
BACKUP_DIR="${BACKUP_DIR:-/backup}"
ARCHIVE_DIR="${ARCHIVE_DIR:-/archive}"

echo "== WAL archiving settings (already switched on in the course container) =="
psql -U postgres -d lab -c "SELECT name, setting FROM pg_settings
                            WHERE name IN ('wal_level','archive_mode','archive_command') ORDER BY name"

echo "== Base backup: pg_basebackup -D $BACKUP_DIR/base -Fp -X stream -c fast -P =="
rm -rf "$BACKUP_DIR/base"
pg_basebackup -U postgres -D "$BACKUP_DIR/base" -Fp -X stream -c fast -P
echo "Base backup finished at: $(date '+%Y-%m-%d %H:%M:%S %Z')"
du -sh "$BACKUP_DIR/base" | awk '{print "Base backup size: " $1}'

echo
echo "== Verify the backup against its manifest =="
pg_verifybackup -n "$BACKUP_DIR/base"

echo
echo "== Make sure WAL keeps flowing into the archive =="
psql -U postgres -d lab -tAc "SELECT pg_switch_wal()" >/dev/null
sleep 2
psql -U postgres -d lab -c "SELECT archived_count, last_archived_wal, failed_count FROM pg_stat_archiver"
echo "Archived WAL files in $ARCHIVE_DIR: $(ls "$ARCHIVE_DIR" | wc -l)"
