# CE 502 lab image: PostgreSQL 16 + pgvector, prepared for Weeks 1-2
#   - WAL archiving switched on, so Week 2 can practise point-in-time recovery
#   - /archive (archived WAL) and /backup (backups) owned by the postgres user
#   - a "replicator" role for the optional streaming-replication demo
FROM pgvector/pgvector:0.8.0-pg16

RUN mkdir -p /archive /backup \
 && chown postgres:postgres /archive /backup \
 && chmod 700 /archive /backup

COPY initdb/ /docker-entrypoint-initdb.d/
COPY replica-entrypoint.sh /usr/local/bin/replica-entrypoint.sh
RUN chmod 755 /usr/local/bin/replica-entrypoint.sh

# Every -c setting can be checked in psql with SHOW, e.g.  SHOW archive_mode;
CMD ["postgres", \
     "-c", "wal_level=replica", \
     "-c", "archive_mode=on", \
     "-c", "archive_command=test ! -f /archive/%f && cp %p /archive/%f", \
     "-c", "max_wal_senders=10", \
     "-c", "wal_keep_size=256MB", \
     "-c", "log_checkpoints=on"]
