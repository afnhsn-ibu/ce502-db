"""CE 502 · Practice 3 · Part B: a lost update in real application code, and two fixes.

Two "cashiers" (threads) each add 1 to the same balance 200 times.
Correct final balance: 100 + 2 x 200 = 500.

Usage:  python labs/week03/python/lost_update_threads.py
        PGDSN="postgresql://postgres:lab@localhost:5433/lab" python ...   (another port)
"""
import os
import threading

import psycopg

DSN = os.environ.get("PGDSN", "postgresql://postgres:lab@localhost:5432/lab")
N = 200


def reset():
    with psycopg.connect(DSN, autocommit=True) as c:
        c.execute("DROP TABLE IF EXISTS acc")
        c.execute("CREATE TABLE acc (id int PRIMARY KEY, bal int NOT NULL)")
        c.execute("INSERT INTO acc VALUES (1, 100)")


def cashier(mode):
    with psycopg.connect(DSN) as conn:          # each thread has its own connection
        for _ in range(N):
            with conn.transaction():
                if mode == "naive":
                    # read, compute in Python, write back: the classic lost update
                    bal = conn.execute("SELECT bal FROM acc WHERE id = 1").fetchone()[0]
                    conn.execute("UPDATE acc SET bal = %s WHERE id = 1", (bal + 1,))
                elif mode == "for_update":
                    # fix 1: lock the row while reading it (pessimistic)
                    bal = conn.execute("SELECT bal FROM acc WHERE id = 1 FOR UPDATE").fetchone()[0]
                    conn.execute("UPDATE acc SET bal = %s WHERE id = 1", (bal + 1,))
                else:
                    # fix 2: let the database do the arithmetic atomically
                    conn.execute("UPDATE acc SET bal = bal + 1 WHERE id = 1")


def run(mode):
    reset()
    threads = [threading.Thread(target=cashier, args=(mode,)) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    with psycopg.connect(DSN) as c:
        final = c.execute("SELECT bal FROM acc WHERE id = 1").fetchone()[0]
    lost = 100 + 2 * N - final
    print(f"{mode:<11} final balance = {final:>4}   expected = {100 + 2 * N}   lost updates = {lost}")


if __name__ == "__main__":
    for mode in ("naive", "for_update", "atomic"):
        run(mode)
