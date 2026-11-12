# Setup · CE 502 Lab Environment

Do this **before the Week 1 class**. It takes about 20 minutes, mostly waiting for the first image download (about 150 MB).

You need:

- **Docker:** Docker Desktop on Windows or macOS, or Docker Engine with the Compose plugin on Linux.
- **About 2 GB** of free disk space for Weeks 1–8. Week 9 adds MongoDB and Cassandra (about 1.5 GB more disk and **at least 4 GB RAM** for Docker). Weeks 10–12 add Python AI packages (about 2 GB).
- **Python 3.10+** from Week 3 on (optional in Week 1).

You do **not** need to install PostgreSQL. Everything runs in a container.

## 1. Install Docker

| System | What to do |
|---|---|
| Windows 10/11 | Install **Docker Desktop** and accept the WSL 2 option. Restart, then start Docker Desktop and wait for "Engine running". |
| macOS (Intel or Apple silicon) | Install **Docker Desktop** and start it. |
| Linux | Install Docker Engine and the `docker-compose-plugin` package, then `sudo usermod -aG docker $USER`, then log out and back in. |

Check in a terminal (PowerShell on Windows):

```bash
docker --version
docker compose version
```

## 2. Get the kit and start the container

Unzip the kit, or clone the course repository, and open a terminal **in the kit's root folder**, the one that contains `docker-compose.yml`:

```bash
docker compose up -d --build
docker compose ps
```

Wait until `ce502-postgres` shows **healthy**. The first build downloads the PostgreSQL 16 + pgvector image.

What the build adds to the standard image (see `docker/postgres/Dockerfile`):

- WAL archiving switched on (`wal_level=replica`, `archive_mode=on`), for Week 2;
- the folders `/archive` and `/backup` owned by the `postgres` user, kept in Docker volumes;
- a `replicator` role, for the optional replication demo in Lesson 2-2.

## 3. Check that everything works

```bash
docker exec -u postgres ce502-postgres bash /kit/setup/check_setup.sh
```

Expected:

```
CE 502 setup check
  [ OK ] PostgreSQL 16.x is running
  [ OK ] wal_level = replica
  [ OK ] archive_mode = on
  [ OK ] pg_waldump is available (Week 1)
  [ OK ] pg_basebackup is available (Week 2)
  [ OK ] /archive is writable by postgres
  [ OK ] /backup is writable by postgres
  [ OK ] the kit is mounted at /kit
  [ OK ] extensions vector, dblink and postgres_fdw are available
  [ OK ] WAL archiver has no failures
  [ OK ] replication role exists (Lesson 2-2 demo)
  [ OK ] scripts have Unix line endings

Result: 12 passed, 0 failed.
You are ready for Practices 1-4.
```

**Bring a screenshot of this result to the first class.**

## 4. Connect

| From | How |
|---|---|
| Terminal (no install needed) | `docker exec -it ce502-postgres psql -U postgres -d lab` |
| A GUI tool (DBeaver, pgAdmin, DataGrip) | host `localhost`, port `5432`, database `lab`, user `postgres`, password `lab` |
| Python | `psycopg.connect("host=localhost port=5432 dbname=lab user=postgres password=lab")` |

Useful psql commands:

| Command | What it does |
|---|---|
| `\i /kit/labs/week01/sql/00_setup.sql` | run a kit script |
| `\dt` | list tables |
| `\d lab1` | describe a table |
| `\x` | toggle expanded output |
| `\q` | quit |

The kit folder is mounted **read-only** at `/kit` inside the container. Edit files on your laptop; the container sees the changes immediately.

## 5. Python (from Week 3; optional in Week 1)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r setup/requirements.txt
```

From **Week 10**, also install the AI packages. This includes everything in `requirements.txt`; PyTorch is a large download, so do it on a good connection:

```bash
pip install -r setup/requirements-ai.txt
```

## 6. Extra services for later weeks

| Week | Command | What starts |
|---|---|---|
| 2 (optional demo) | `docker compose --profile replication up -d` | `ce502-replica`, a streaming standby on port 5433 |
| 9, 11 | `docker compose --profile nosql up -d` | `ce502-mongo` (MongoDB 7, port 27017) and `ce502-cassandra` (Cassandra 5, port 9042). Cassandra needs about a minute and 1.5 GB RAM |
| 11 (optional) | `docker compose --profile atlas up -d` | `ce502-atlas`, MongoDB with vector search, port 27018 |

Stop them again with `docker compose --profile nosql down` (or the profile you started) when the week is over, to free memory.

## Everyday commands

| Task | Command |
|---|---|
| Start | `docker compose up -d` |
| Status | `docker compose ps` |
| Server log | `docker compose logs -f postgres` (Ctrl+C to leave) |
| Stop, keeping data | `docker compose down` |
| Stop and **delete all data**, then start fresh | `docker compose down -v`, then `docker compose up -d` |
| Rebuild after the Dockerfile changed | `docker compose up -d --build` |

## Troubleshooting

| Problem | Fix |
|---|---|
| `port is already allocated` / `address already in use` on 5432 | A local PostgreSQL is running. Stop it, or change `"5432:5432"` to `"5435:5432"` in `docker-compose.yml` and use port 5435 from GUI tools. `docker exec` commands are not affected. |
| `Cannot connect to the Docker daemon` | Docker Desktop is not running. Start it and wait for "Engine running". |
| Check fails: `/archive is not writable` or `replication role missing` | Your volumes were created by an older version of the image. Run `docker compose down -v` and `docker compose up -d --build`. |
| Check fails: `the kit is not mounted at /kit` | You ran `docker compose` from another folder. `cd` into the kit's root folder, then `docker compose down` and `docker compose up -d`. |
| Apple silicon: `no matching manifest` | Update Docker Desktop. The image supports arm64. |
| Corporate or university network blocks Docker Hub | Use eduroam or a phone hotspot for the first build, or ask the instructor for the offline image (`docker load -i ce502-postgres.tar`). |

### Windows notes

- Use **PowerShell** or Windows Terminal. All commands in the labs are single `docker …` lines, so they work unchanged.
- If you cloned the repository with Git and the check reports **Windows line endings**, run this once in the kit folder:

  ```bash
  git config core.autocrlf false
  git rm --cached -r .
  git reset --hard
  ```

  The kit's `.gitattributes` prevents this for new clones. Unzipped kits are not affected.
- Keep the kit on a local drive, such as `C:\Users\<you>\ce502`, not on a network or OneDrive folder. Bind mounts from synced folders can be slow or fail.
