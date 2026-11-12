#!/bin/bash
# Runs once, the first time the container creates its database cluster.
set -euo pipefail

# Role used by the replica container (Week 2, Lesson 2-2 demo).
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<SQL
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD '${REPLICATOR_PASSWORD:-replicator}';
SQL

# Allow replication connections from other containers on the Docker network.
echo "host replication replicator all scram-sha-256" >> "$PGDATA/pg_hba.conf"
