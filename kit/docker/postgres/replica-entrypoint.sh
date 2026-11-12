#!/bin/bash
# Start script of the "replica" container (docker compose --profile replication up -d).
# First start: clone the primary with pg_basebackup. Every start: run as a hot standby.
set -euo pipefail
PGDATA="${PGDATA:-/var/lib/postgresql/data}"
PRIMARY_HOST="${PRIMARY_HOST:-postgres}"
PRIMARY_PORT="${PRIMARY_PORT:-5432}"

if [ ! -s "$PGDATA/PG_VERSION" ]; then
  echo "replica: waiting for the primary ($PRIMARY_HOST) ..."
  until pg_isready -h "$PRIMARY_HOST" -p "$PRIMARY_PORT" -U replicator -q; do sleep 2; done
  echo "replica: cloning the primary with pg_basebackup ..."
  # -R writes standby.signal and primary_conninfo, so the copy starts as a standby.
  pg_basebackup -h "$PRIMARY_HOST" -p "$PRIMARY_PORT" -U replicator -D "$PGDATA" -X stream -R -c fast -P
  chmod 700 "$PGDATA"
fi

# cluster_name becomes the replica's application_name on the primary
# (used by synchronous_standby_names in the synchronous-replication demo).
exec postgres -c hot_standby=on -c archive_mode=off -c cluster_name=replica1
