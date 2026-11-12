"""CE 502 · Practice 3 · Runs all four two-session experiments automatically (instructor demo / self-check).

Students should first do the experiments by hand in two psql terminals (sql/e*/session_a.sql, session_b.sql).
Usage:  python labs/week03/python/run_experiments.py
        PGDSN="postgresql://postgres:lab@localhost:5432/lab" python labs/week03/python/run_experiments.py
"""
import os
import sys
import threading
import time

import psycopg

PRINT_LOCK = threading.Lock()


def say(line):
    with PRINT_LOCK:
        sys.stdout.write(line + "\n")
        sys.stdout.flush()


DSN = os.environ.get("PGDSN", "postgresql://postgres:lab@localhost:5432/lab")


def reset():
    with psycopg.connect(DSN, autocommit=True) as c:
        c.execute("DROP TABLE IF EXISTS acc")
        c.execute("CREATE TABLE acc (id int PRIMARY KEY, bal int NOT NULL)")
        c.execute("INSERT INTO acc VALUES (1, 100), (2, 100)")


def balance():
    with psycopg.connect(DSN, autocommit=True) as c:
        return c.execute("SELECT id, bal FROM acc ORDER BY id").fetchall()


class Session:
    """One psql-like session. Statements run in a thread so one session can block while the other continues."""

    def __init__(self, name):
        self.name = name
        self.conn = psycopg.connect(DSN, autocommit=True)  # we send BEGIN/COMMIT ourselves, like psql
        self.thread = None

    def run(self, sql, wait=True):
        self.join()  # a session runs one statement at a time, like psql
        def work():
            try:
                cur = self.conn.execute(sql)
                rows = cur.fetchall() if cur.description else None
                say(f"  {self.name}: {sql:<55} -> {rows if rows is not None else cur.statusmessage}")
            except psycopg.Error as e:
                say(f"  {self.name}: {sql:<55} -> ERROR: {e.diag.message_primary}")
        self.thread = threading.Thread(target=work)
        self.thread.start()
        if wait:
            self.thread.join(timeout=0.5)
            if self.thread.is_alive():
                say(f"  {self.name}: ... waiting (blocked by a lock)")

    def join(self):
        if self.thread:
            self.thread.join()

    def close(self):
        self.conn.close()


def experiment(title, steps, level="READ COMMITTED"):
    print(f"\n=== {title} [{level}] ===")
    reset()
    a, b = Session("A"), Session("B")
    for who, sql in steps:
        s = a if who == "A" else b
        s.run(sql.replace("{LEVEL}", level))
        time.sleep(0.2)
    time.sleep(1.5)  # let deadlock detection (deadlock_timeout = 1 s) finish
    a.join(); b.join()
    print("  final:", balance())
    a.close(); b.close()


DEADLOCK = [("A", "BEGIN"), ("B", "BEGIN"),
            ("A", "UPDATE acc SET bal = bal - 10 WHERE id = 1"),
            ("B", "UPDATE acc SET bal = bal - 10 WHERE id = 2"),
            ("A", "UPDATE acc SET bal = bal + 10 WHERE id = 2"),
            ("B", "UPDATE acc SET bal = bal + 10 WHERE id = 1"),
            ("A", "COMMIT"), ("B", "COMMIT")]

NONREPEATABLE = [("A", "BEGIN ISOLATION LEVEL {LEVEL}"),
                 ("A", "SELECT bal FROM acc WHERE id = 1"),
                 ("B", "UPDATE acc SET bal = 500 WHERE id = 1"),
                 ("A", "SELECT bal FROM acc WHERE id = 1"),
                 ("A", "COMMIT")]

LOST_UPDATE = [("A", "BEGIN ISOLATION LEVEL {LEVEL}"), ("B", "BEGIN ISOLATION LEVEL {LEVEL}"),
               ("A", "SELECT bal FROM acc WHERE id = 1"),
               ("B", "SELECT bal FROM acc WHERE id = 1"),
               ("A", "UPDATE acc SET bal = 150 WHERE id = 1"),
               ("A", "COMMIT"),
               ("B", "UPDATE acc SET bal = 150 WHERE id = 1"),
               ("B", "COMMIT")]

PHANTOM = [("A", "BEGIN ISOLATION LEVEL {LEVEL}"),
           ("A", "SELECT count(*) FROM acc WHERE bal >= 100"),
           ("B", "INSERT INTO acc VALUES (3, 300)"),
           ("A", "SELECT count(*) FROM acc WHERE bal >= 100"),
           ("A", "COMMIT")]

WRITE_SKEW = [("A", "BEGIN ISOLATION LEVEL {LEVEL}"), ("B", "BEGIN ISOLATION LEVEL {LEVEL}"),
              ("A", "SELECT sum(bal) FROM acc"),
              ("B", "SELECT sum(bal) FROM acc"),
              ("A", "UPDATE acc SET bal = 0 WHERE id = 1"),
              ("B", "UPDATE acc SET bal = 0 WHERE id = 2"),
              ("A", "COMMIT"),
              ("B", "COMMIT")]

if __name__ == "__main__":
    experiment("E1 Deadlock", DEADLOCK)
    for lvl in ("READ COMMITTED", "REPEATABLE READ"):
        experiment("E2 Non-repeatable read", NONREPEATABLE, lvl)
    for lvl in ("READ COMMITTED", "REPEATABLE READ"):
        experiment("E3 Lost update (app computes 100 + 50)", LOST_UPDATE, lvl)
    for lvl in ("READ COMMITTED", "REPEATABLE READ"):
        experiment("E4 Phantom read", PHANTOM, lvl)
    for lvl in ("REPEATABLE READ", "SERIALIZABLE"):
        experiment("E5 Write skew (optional)", WRITE_SKEW, lvl)
