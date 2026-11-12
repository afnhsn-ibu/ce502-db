"""
CE 502 · Practice 1 · Extension (optional): what does a COMMIT cost?

At every COMMIT the DBMS must flush the log buffer to disk before it can say "committed"
(the write-ahead rule + durability). This script inserts the same rows three ways and measures
the time and the WAL each way produces:

  1. one transaction per row   (N commits -> N log flushes)
  2. one transaction for all   (1 commit  -> 1 log flush)
  3. one transaction per row with synchronous_commit = off
     (commits return before the flush: faster, but the last few commits can be lost in a crash)

Run from your laptop (Python 3.10+):
    pip install -r setup/requirements.txt
    python labs/week01/python/commit_cost.py            # default 2,000 rows
    python labs/week01/python/commit_cost.py --rows 5000
Connection settings can be changed with --dsn or the PG* environment variables.
"""
import argparse
import time

import psycopg

DEFAULT_DSN = "host=localhost port=5432 dbname=lab user=postgres password=lab"


def wal_lsn(cur):
    cur.execute("SELECT pg_current_wal_lsn()")
    return cur.fetchone()[0]


def wal_bytes(cur, start, end):
    cur.execute("SELECT pg_wal_lsn_diff(%s, %s)", (end, start))
    return int(cur.fetchone()[0])


def run(conn, label, rows, per_row_commit, sync_commit):
    with conn.cursor() as cur:
        cur.execute("TRUNCATE commit_test")
        conn.commit()
        cur.execute(f"SET synchronous_commit = {sync_commit}")
        conn.commit()
        start_lsn = wal_lsn(cur)
        conn.commit()

        t0 = time.perf_counter()
        for i in range(rows):
            cur.execute("INSERT INTO commit_test VALUES (%s, %s)", (i, f"row {i}"))
            if per_row_commit:
                conn.commit()
        conn.commit()
        elapsed = time.perf_counter() - t0

        end_lsn = wal_lsn(cur)
        conn.commit()
        wal = wal_bytes(cur, start_lsn, end_lsn)
        cur.execute("SET synchronous_commit = on")
        conn.commit()
    print(f"{label:<44} {elapsed:8.3f} s {rows / elapsed:10.0f} rows/s {wal / 1024:10.1f} kB WAL")
    return elapsed


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dsn", default=DEFAULT_DSN, help="libpq connection string")
    parser.add_argument("--rows", type=int, default=2000, help="rows to insert in each run")
    args = parser.parse_args()

    with psycopg.connect(args.dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS commit_test")
            cur.execute("CREATE TABLE commit_test (id int PRIMARY KEY, v text)")
        conn.commit()

        print(f"Inserting {args.rows:,} rows three ways\n")
        print(f"{'Method':<44} {'time':>10} {'speed':>16} {'log':>13}")
        a = run(conn, "1. COMMIT after every row", args.rows, True, "on")
        b = run(conn, "2. one transaction, one COMMIT", args.rows, False, "on")
        c = run(conn, "3. COMMIT every row, synchronous_commit=off", args.rows, True, "off")

        print(f"\nOne big transaction was {a / b:.1f}x faster than committing every row.")
        print(f"synchronous_commit=off was {a / c:.1f}x faster than the default, at a durability cost.")
        print("Questions: why does method 1 write more WAL than method 2? Which method would you use")
        print("to load a nightly file, and which for a bank transfer? Explain using the write-ahead rule.")

        with conn.cursor() as cur:
            cur.execute("DROP TABLE commit_test")
        conn.commit()


if __name__ == "__main__":
    main()
