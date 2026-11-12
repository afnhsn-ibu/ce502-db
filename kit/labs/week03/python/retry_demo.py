"""
CE 502 · Practice 3 · Report item 5 helper (optional): how an application handles
"deadlock detected" (SQLSTATE 40P01) and "could not serialize access" (SQLSTATE 40001).

Both errors mean: "your transaction was rolled back so that the others stay correct;
run the WHOLE transaction again". This script runs the E3 lost-update pattern
(read the balance, add 1 in Python, write it back) in two threads at REPEATABLE READ.
Without retries, many transactions fail. With a retry loop, every increment is applied.

Usage:  python labs/week03/python/retry_demo.py
"""
import os
import random
import threading
import time

import psycopg
from psycopg import errors

DSN = os.environ.get("PGDSN", "postgresql://postgres:lab@localhost:5432/lab")
N = 100                      # increments per thread
MAX_ATTEMPTS = 20            # with exponential back-off this allows several seconds of retrying
RETRYABLE = (errors.SerializationFailure, errors.DeadlockDetected)   # 40001, 40P01


def reset():
    with psycopg.connect(DSN, autocommit=True) as c:
        c.execute("DROP TABLE IF EXISTS acc")
        c.execute("CREATE TABLE acc (id int PRIMARY KEY, bal int NOT NULL)")
        c.execute("INSERT INTO acc VALUES (1, 100)")


def add_one(conn):
    """One business transaction: read, compute in Python, write back."""
    with conn.transaction():
        conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        bal = conn.execute("SELECT bal FROM acc WHERE id = 1").fetchone()[0]
        conn.execute("UPDATE acc SET bal = %s WHERE id = 1", (bal + 1,))


def worker(retry, stats):
    with psycopg.connect(DSN) as conn:
        for _ in range(N):
            attempt = 0
            while True:
                attempt += 1
                try:
                    add_one(conn)
                    stats["ok"] += 1
                    break
                except RETRYABLE:
                    stats["errors"] += 1
                    if not retry or attempt == MAX_ATTEMPTS:
                        stats["gave_up"] += 1
                        break
                    # exponential back-off with jitter (5 ms, 10 ms, 20 ms, ... capped at 0.5 s),
                    # so the two threads do not collide again at once
                    time.sleep(random.uniform(0, min(0.5, 0.005 * 2 ** (attempt - 1))))


def run(retry):
    reset()
    stats = {"ok": 0, "errors": 0, "gave_up": 0}
    threads = [threading.Thread(target=worker, args=(retry, stats)) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    with psycopg.connect(DSN) as c:
        final = c.execute("SELECT bal FROM acc WHERE id = 1").fetchone()[0]
    label = "with retry loop" if retry else "no retry"
    print(f"{label:<16} final = {final:>4} (expected {100 + 2 * N})   "
          f"40001/40P01 errors = {stats['errors']:>3}   increments given up = {stats['gave_up']}")


if __name__ == "__main__":
    run(retry=False)
    run(retry=True)
    print("\nNo update is ever lost at REPEATABLE READ: a conflicting transaction fails instead.")
    print("The application's job is to catch 40001/40P01 and run the whole transaction again.")
