# Practice 2 · You Are the DBA During an Incident

**CE 502 · Week 2** · Individual · about 60 minutes (Part B: +30 minutes) · 10 points + 2 bonus
**Lessons:** 2-1 Database Backups, 2-3 Database Recovery
**Submit:** a report of one to two pages as PDF, before the Week 3 class. Use `report-template.md` and `runbook-template.md`.

You protect a small shop database. You take a backup, simulate a mistake that destroys data, and bring the lost data back. You also measure how long this takes and how much data could be lost: your **RTO** and **RPO**.

| Part | What you do | Lesson objective |
|---|---|---|
| Setup | Create `shop` with 5,000 customers and 50,000 orders | – |
| A | Logical backup with `pg_dump`, an accidental `DELETE`, a timed restore with `pg_restore` into a new database | 2-1 O3, O4 · 2-3 O3 |
| B (bonus) | Physical base backup + archived WAL, a `DROP TABLE`, and **point-in-time recovery** | 2-1 O4 · 2-3 O2 |
| Demo (optional) | Streaming replication, synchronous vs asynchronous, failover, "replication is not backup": see `replication-demo/README.md` | 2-2 O1–O4 |

---

## Before you start

```bash
docker compose up -d
docker exec -u postgres ce502-postgres bash /kit/setup/check_setup.sh     # all [ OK ]
```

In this practice almost everything is a single command you run from your laptop's terminal. There are two forms:

- **SQL scripts:** `docker exec -it ce502-postgres psql -U postgres -d <db> -f /kit/labs/week02/sql/<file>.sql`
- **Shell scripts:** `docker exec -u postgres ce502-postgres bash /kit/labs/week02/scripts/<file>.sh`

Shell scripts run *inside* the container as the `postgres` user, where `pg_dump`, `pg_restore` and `pg_basebackup` are installed. Backups go to the container's `/backup` volume and archived WAL to `/archive`. Both survive a container restart.

### Setup (3 minutes)

```bash
docker exec -it ce502-postgres psql -U postgres -d lab -f /kit/labs/week02/sql/00_create_shop.sql
```

Expected:

```
 customers | orders | total_amount | database_size
-----------+--------+--------------+---------------
      5000 |  50000 |  12630282.36 | 11 MB
```

`setseed` makes the data the same for everyone, so your counts and total should match exactly. **Write the total amount down.** You will use it to prove that a restore is complete.

---

## Part A · Logical backup and restore (40 min)

### Step 1 · Take a logical backup

```bash
docker exec -u postgres ce502-postgres bash /kit/labs/week02/scripts/01_logical_backup.sh
```

The script runs `pg_dump -U postgres -Fc -d shop -f /backup/shop.dump`, times it, and lists the dump's contents:

```
Backup time: 0.168 s
Backup finished at: 2026-10-25 23:50:54 CET   <- write this down (it decides your RPO)
Dump file size: 539K

215; 1259 16452 TABLE public customers postgres
217; 1259 16460 TABLE public orders postgres
...
3403; 0 16460 TABLE DATA public orders postgres
...
3257; 2606 16467 FK CONSTRAINT public orders orders_customer_id_fkey postgres
```

- `-Fc` means **custom format**: compressed, and `pg_restore` can restore all of it or only chosen tables.
- The table of contents shows that a logical backup stores **definitions + data**, not data files. Indexes and constraints are rebuilt during restore.
- Compare the dump size (≈0.5 MB) with the database size (11 MB). Why is it so much smaller?

### Step 2 · The accident

A script meant for a test database runs against production:

```bash
docker exec -it ce502-postgres psql -U postgres -d shop -f /kit/labs/week02/sql/02_accident.sql
```

```
DELETE 25000
 orders_after
--------------
        25000
```

The DELETE ran in autocommit mode, so it is **committed**. ROLLBACK cannot help any more. This is a **human error**, not a system failure. Crash recovery cannot repair it: from the DBMS's point of view, a valid transaction committed correctly. Only a copy taken *before* the mistake can bring the rows back.

### Steps 3–4 · Restore into a new database, and time it

```bash
docker exec -u postgres ce502-postgres bash /kit/labs/week02/scripts/03_restore.sh
```

The script does what the slide shows:

```bash
createdb -U postgres shop_restored
time pg_restore -U postgres -d shop_restored /backup/shop.dump
```

It then compares both databases:

```
Restore time: 0.126 s

shop            orders: 25000   total amount: 6330127.88
shop_restored   orders: 50000   total amount: 12630282.36
```

> **Common mistake:** restoring over the damaged database. Always restore into a **new** database first, check it (counts, totals, a few business queries), and only then switch the application to it or copy rows back. If the backup itself is bad, you have not destroyed the only copy you still had.

**Your measured RTO.** The restore time is one part of your recovery time objective. A real RTO also includes noticing the problem, deciding what to do, checking the copy, and switching the application. In the report, list these parts and estimate each one.

### Step 5 (optional) · Repair only what was lost

Instead of switching to `shop_restored`, copy back just the deleted rows:

```bash
docker exec -it ce502-postgres psql -U postgres -d shop -f /kit/labs/week02/sql/03_repair_from_restored.sql
```

```
INSERT 0 25000
 orders_after_repair | total_amount
---------------------+--------------
               50000 |  12630282.36
```

The total matches your setup value, so the repair is complete. Now think about the gap. Suppose the backup ran at 02:00, the DELETE happened at 16:00, and customers placed 300 orders between those times. Every one of those orders that the DELETE removed is **gone**: it is not in the dump, and the database no longer has it. With a nightly dump, the **RPO is up to 24 hours**. Part B closes this gap.

---

## Part B (bonus, +2) · Point-in-time recovery (30 min)

A logical dump is a photograph. **Point-in-time recovery (PITR)** combines a *physical* base backup with *every* WAL file written since. It can rebuild the database as it was at any second, for example one second before a mistake.

### Step 1 · Check archiving, take a base backup

In the course container, WAL archiving is already on (see `docker/postgres/Dockerfile`):

```
wal_level       = replica
archive_mode    = on
archive_command = 'test ! -f /archive/%f && cp %p /archive/%f'
```

On your own server you would set these in `postgresql.conf` and restart. Here, just check them and take the backup:

```bash
docker exec -u postgres ce502-postgres bash /kit/labs/week02/scripts/04_base_backup.sh
```

```
 archive_command | test ! -f /archive/%f && cp %p /archive/%f
 archive_mode    | on
 wal_level       | replica
Base backup finished at: 2026-10-25 23:51:01 CET
Base backup size: 80M
backup successfully verified
 archived_count |            last_archived_wal             | failed_count
----------------+------------------------------------------+--------------
              6 | 000000010000000000000005.00000028.backup |            0
```

`pg_basebackup -Fp -X stream -c fast` copies the **data files** of the whole server, plus the WAL needed to make them consistent. `pg_verifybackup` checks every file against the backup manifest. Why is the base backup (80 MB) much bigger than the dump (0.5 MB)?

### Step 2 · New work, a target time, then the disaster

```bash
docker exec -it ce502-postgres psql -U postgres -d shop -f /kit/labs/week02/sql/05_work_then_disaster.sql
```

The script:

1. inserts 3 new orders **after** the base backup;
2. prints a **recovery target time**;
3. waits two seconds;
4. runs `DROP TABLE orders`;
5. forces a WAL switch so that the last WAL file is archived.

```
 orders_now | newest_order
------------+--------------
      50003 |        50003

>>> RECOVERY TARGET TIME (copy this exactly): 2026-10-25 23:51:05 CET

DROP TABLE
orders has been dropped.
```

Copy **your** target time, including the time zone.

### Step 3 · Recover to that time, on a second server

```bash
docker exec -u postgres ce502-postgres bash /kit/labs/week02/scripts/06_pitr_restore.sh "2026-10-25 23:51:05 CET"
```

Following the "restore somewhere new first" rule, the script does **not** overwrite the live server. It builds a second server inside the container, on port 5434:

1. It copies `/backup/base` to `/backup/pitr`.
2. It adds the recovery settings:

   ```
   restore_command      = 'cp /archive/%f %p'          # where to fetch archived WAL from
   recovery_target_time = '2026-10-25 23:51:05 CET'   # where to stop
   recovery_target_action = 'promote'                 # then open for normal use
   ```

3. It creates the empty file `recovery.signal`, which means "start in recovery mode".
4. It starts the server with `pg_ctl`, waits until recovery has finished, and shows the server log and the result:

```
Recovery time (start + replay): 0.532 s
LOG:  starting point-in-time recovery to 2026-10-25 23:51:05+01
LOG:  restored log file "000000010000000000000005" from archive
LOG:  restored log file "000000010000000000000006" from archive
LOG:  recovery stopping before commit of transaction 4840, time 2026-10-25 23:51:07.414395+01
LOG:  selected new timeline ID: 2
LOG:  archive recovery complete

 orders | newest_order | total_amount
--------+--------------+--------------
  50003 |        50003 |  12630949.02
Compare with the live server, where orders no longer exists:
f
```

How to read these lines:

- **restored log file …**: archived WAL is replayed on top of the base backup. This is the redo phase from Lesson 1-3, now driven by the archive.
- **recovery stopping before commit of transaction 4840**: transaction 4840 is the `DROP TABLE`. Its commit time (23:51:07) is after the target, so it is not replayed.
- **50003 orders**: everything up to the target is back, *including the 3 orders written after the base backup*. A nightly dump would have lost them.
- **new timeline ID: 2**: the recovered server's history branches off here. Its future WAL cannot be confused with the old history, in which the table was dropped.

> **Critical:** `recovery_target_time` must be **before** the mistake. If you choose a later time, the DROP is replayed as well and the table is gone again. If that happens, run the script again with an earlier time. The base backup and the archive are unchanged.

To look around in the recovered server:

```bash
docker exec -it -u postgres ce502-postgres psql -p 5434 -d shop
```

### Clean up

```bash
docker exec -u postgres ce502-postgres bash /kit/labs/week02/scripts/07_cleanup_pitr.sh
```

To repeat the whole practice from the beginning, run the setup again. The live server's `shop` database is still missing `orders` until you do.

---

## What to submit

One to two pages as PDF, from `report-template.md`, plus your runbook from `runbook-template.md`:

| Report item | Points |
|---|---|
| Part A: backup time, dump file size and restore time | 2 |
| Part A: row counts before and after, with one sentence of interpretation | 2 |
| Your measured RTO, and the RPO of a nightly pg_dump | 2 |
| A recovery runbook of 5–8 numbered steps | 2 |
| Bonus, Part B: recovered table and the recovery lines from the server log | +2 |
| **Total** | **10 (+2)** |

**Key point:** every number in the report needs one sentence that says what it proves.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `database "shop" does not exist` | Run the setup (`00_create_shop.sql`). |
| `pg_dump: error: … permission denied` for `/backup` | The volume was created by an older image. Run `docker compose down -v`, then `docker compose up -d --build`. |
| `could not open file "/archive/…"` in `/backup/pitr.log` | The WAL file with the DROP was not archived yet. Run `docker exec -it ce502-postgres psql -U postgres -d lab -c "SELECT pg_switch_wal()"`, wait 5 seconds and run `06_pitr_restore.sh` again. |
| PITR result has **no** `orders` table | Your target time is after the DROP, or it has the wrong time zone. Use the exact value that step 2 printed. |
| `recovery ended before configured recovery target was reached` | Your target time is later than the last archived WAL. Force a WAL switch (see above) and retry. |
| `pg_ctl: another server might be running` | Run `07_cleanup_pitr.sh` and try again. |
| Port 5434 already in use | Only one recovered server can run at a time. Run `07_cleanup_pitr.sh`. |

## Going further (optional)

- **Size changes everything.** Insert 2 million more orders (`INSERT INTO orders (customer_id, amount) SELECT 1 + g % 5000, 10 FROM generate_series(1, 2000000) g;`). Repeat steps 1 and 3–4. How do the backup and restore times grow? Extrapolate to the 400 GB registry database from the Lesson 2-3 case study.
- **Parallel restore.** Repeat step 4 with `pg_restore -j 4 …`. What changes and why?
- **One table only.** Restore only `orders` from the dump: `pg_restore -t orders -d shop_restored …`.
