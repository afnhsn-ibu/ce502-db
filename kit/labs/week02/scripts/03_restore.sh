#!/usr/bin/env bash
# CE 502 · Practice 2 · Part A · Steps 3-4: restore the dump into a NEW database, time it, compare.
# Run: docker exec -u postgres ce502-postgres bash /kit/labs/week02/scripts/03_restore.sh
set -euo pipefail
BACKUP_DIR="${BACKUP_DIR:-/backup}"

echo "== Step 3: create an empty database to restore into =="
dropdb  -U postgres --if-exists shop_restored
createdb -U postgres shop_restored

echo "== Step 4: restore and time it (this time is your measured RTO) =="
START=$(date +%s%N)
pg_restore -U postgres -d shop_restored "$BACKUP_DIR/shop.dump"
END=$(date +%s%N)
MS=$(( (END - START) / 1000000 ))
printf "Restore time: %d.%03d s\n" $((MS / 1000)) $((MS % 1000))

echo
echo "== Compare the damaged database with the restored copy =="
for db in shop shop_restored; do
  psql -U postgres -d "$db" -tAc \
    "SELECT rpad('$db', 15) || ' orders: ' || count(*) || '   total amount: ' || sum(amount) FROM orders"
done
echo
echo "Restored into shop_restored, NOT over shop. Check it first; then switch the application,"
echo "or copy back only the missing rows (see the README, step 5)."
