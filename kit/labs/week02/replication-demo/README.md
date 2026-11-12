# Replication Demo · Lesson 2-2

**CE 502 · Week 2** · Optional, not marked · about 30 minutes
Your instructor runs it live in Lesson 2-2. You can repeat it at home.

This demo makes the four objectives of Lesson 2-2 visible:

| Part | You see | Objective |
|---|---|---|
| 1 | A second server that copies the primary by streaming its WAL | O1 · replication uses the log |
| 2 | Synchronous replication: a COMMIT that waits, and hangs when the replica is down | O2 · synchronous vs asynchronous |
| 3 | A DELETE on the primary that arrives on the replica within a second | O4 · replication is not a backup |
| 4 | Failover: the replica becomes the primary; split brain if the old primary returns | O3 · failover and split brain |

```
 laptop:5432 ──► ce502-postgres (primary)  ── WAL stream ──►  ce502-replica (hot standby) ◄── laptop:5433
                 /archive, /backup                             read-only, cluster_name = replica1
```

## Start the replica

From the kit's root folder:

```bash
docker compose --profile replication up -d
docker compose ps                       # both containers "healthy" after about 20 s
docker compose logs replica | tail -5   # "started streaming WAL from primary at …"
```

On its first start, the replica runs `pg_basebackup -R`: a physical copy of the primary, plus the settings that make it a standby (`standby.signal` and `primary_conninfo`). See `docker/postgres/replica-entrypoint.sh`. On every later start, it continues streaming from where it stopped.

Two shortcuts make the commands below shorter. **P** runs psql on the primary and **R** runs psql on the replica:

```bash
# P = docker exec -it ce502-postgres psql -U postgres -d lab
# R = docker exec -it ce502-replica  psql -U postgres -d lab
```

---

## Part 1 · Replication uses the log

```bash
docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week02/replication-demo/01_primary_status.sql
```

```
 application_name | client_addr | state     | sync_state | sent_lsn  | write_lsn | flush_lsn | replay_lsn | replay_gap | replay_lag
------------------+-------------+-----------+------------+-----------+-----------+-----------+------------+------------+------------
 replica1         | 172.18.0.3  | streaming | async      | 0/A000060 | 0/A000060 | 0/A000060 | 0/A000060  | 0 bytes    | 00:00:00.026
```

The four LSN columns are the journey of the log: **sent** by the primary, **written** and **flushed** to disk on the replica, then **replayed** into the replica's data files. These are the same records you read with pg_waldump in Practice 1.

Write on the primary, then read on the replica:

```bash
docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week02/replication-demo/03_write_on_primary.sql
docker exec -it ce502-replica  psql -U postgres -d lab -f /kit/labs/week02/replication-demo/02_replica_status.sql
docker exec -it ce502-replica  psql -U postgres -d lab -f /kit/labs/week02/replication-demo/04_read_on_replica.sql
```

```
 is_standby | received_up_to | replayed_up_to | last_replayed_commit          | approx_lag
------------+----------------+----------------+-------------------------------+------------
 t          | 0/A025708      | 0/A025708      | 2026-10-25 23:52:45.191554+01 | 00:00:00

 id |                note                | ...
  1 | written on the primary at 23:52:45 | ...
ERROR:  cannot execute INSERT in a read-only transaction
```

The row is on the replica, but the replica refuses writes. A **hot standby** can serve read-only queries, such as reports, while it waits to take over.

---

## Part 2 · Synchronous vs asynchronous

By default replication is **asynchronous**: the primary reports COMMIT as soon as its *own* log is on disk. Make it **synchronous**:

```bash
docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week02/replication-demo/05_sync_on.sql
```

```
 application_name | sync_state
------------------+------------
 replica1         | sync
```

Every COMMIT now waits until `replica1` has the commit record on disk too. Now stop the replica and try to write:

```bash
docker stop ce502-replica
docker exec -it ce502-postgres psql -U postgres -d lab -c "INSERT INTO repl_demo (note) VALUES ('sync test')"
```

The command **hangs**. The primary will not confirm a commit that only one copy holds. After a few seconds, press **Ctrl+C**:

```
Cancel request sent
WARNING:  canceling wait for synchronous replication due to user request
DETAIL:  The transaction has already committed locally, but might not have been replicated to the standby.
INSERT 0 1
```

This is the trade-off from the lesson. Synchronous replication gives **RPO = 0**: no confirmed commit exists on only one server. The price is availability: if the only synchronous standby is down, writes stop. Production systems therefore use two or more standbys, for example `synchronous_standby_names = 'ANY 1 (s1, s2)'`.

Start the replica again and switch back to asynchronous:

```bash
docker start ce502-replica
docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week02/replication-demo/06_sync_off.sql
```

---

## Part 3 · Replication is not a backup

```bash
docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week02/replication-demo/07_mistake_on_primary.sql
docker exec -it ce502-replica  psql -U postgres -d lab -c "SELECT count(*) AS rows_on_replica FROM repl_demo"
```

```
DELETE 2
 rows_on_replica
-----------------
               0
```

The replica faithfully replayed the DELETE. Replication protects against a failed **server**, not against a wrong **command**. Only a backup, ideally with an archived log for point-in-time recovery as in Practice 2 Part B, can undo it.

---

## Part 4 · Failover, and how split brain happens

**Failover.** The primary "fails":

```bash
docker stop ce502-postgres
docker exec -it ce502-replica psql -U postgres -d lab -c "SELECT pg_promote()"
docker exec -it ce502-replica psql -U postgres -d lab -f /kit/labs/week02/replication-demo/08_after_failover.sql
```

```
 still_standby
---------------
 f
INSERT 0 1
 id |                   note                    | ...
 34 | written on the NEW primary after failover | ...
```

The replica is now a primary and accepts writes. In a real system, an HA manager such as Patroni would promote it and move the application's connection address to it.

Why does the new row have `id` 34 and not 3? The primary logs sequence values in advance, 32 at a time. The promoted replica continues *after* the logged block, so it never hands out a number the old primary may already have used. Gaps are normal and harmless.

**Split brain (watch, do not do this in production).** Start the old primary again:

```bash
docker start ce502-postgres
docker exec -it ce502-postgres psql -U postgres -d lab -c "INSERT INTO repl_demo (note) VALUES ('written on the OLD primary')"
```

Both servers now accept writes and their data drifts apart. Neither knows about the other's changes. This is **split brain**. Real HA systems prevent it in two ways:

- **fencing:** the old primary is stopped before the new one is promoted;
- **consensus:** a majority vote, as in Raft from this week's papers, decides who the single leader is.

---

## Reset

The replica has been promoted, so it can no longer follow the primary. Delete it and start again:

```bash
docker compose --profile replication down      # stops both containers, keeps the primary's data
docker volume rm ce502_replicadata             # deletes the old replica
docker compose up -d                           # primary only, for the labs
```

Next time you run `docker compose --profile replication up -d`, a fresh replica is cloned.

> The primary's `repl_demo` table is not used by any lab. It is safe to leave it or `DROP TABLE repl_demo;`.
