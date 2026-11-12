#!/usr/bin/env bash
# CE 502 · Check that the lab container is ready for Weeks 1-4.
# Run from your laptop:
#   docker exec -u postgres ce502-postgres bash /kit/setup/check_setup.sh
PASS=0; FAIL=0
ok()   { echo "  [ OK ] $1"; PASS=$((PASS+1)); }
bad()  { echo "  [FAIL] $1"; FAIL=$((FAIL+1)); }
q()    { psql -U postgres -d lab -tAc "$1" 2>/dev/null; }

echo "CE 502 setup check"
v=$(q "SHOW server_version")
[[ "$v" == 16* ]] && ok "PostgreSQL $v is running" || bad "PostgreSQL 16 is not reachable (got: '${v:-nothing}')"
[[ "$(q 'SHOW wal_level')" == "replica" ]] && ok "wal_level = replica" || bad "wal_level is not replica"
[[ "$(q 'SHOW archive_mode')" == "on" ]] && ok "archive_mode = on" || bad "archive_mode is not on"
command -v pg_waldump >/dev/null && ok "pg_waldump is available (Week 1)" || bad "pg_waldump not found on PATH"
command -v pg_basebackup >/dev/null && ok "pg_basebackup is available (Week 2)" || bad "pg_basebackup not found on PATH"
[[ -w /archive ]] && ok "/archive is writable by postgres" || bad "/archive is not writable: rebuild with  docker compose build --no-cache"
[[ -w /backup ]]  && ok "/backup is writable by postgres"  || bad "/backup is not writable: rebuild with  docker compose build --no-cache"
[[ -f /kit/labs/week01/README.md ]] && ok "the kit is mounted at /kit" || bad "the kit is not mounted at /kit: run docker compose from the kit's root folder"
[[ "$(q "SELECT count(*) FROM pg_available_extensions WHERE name IN ('vector','dblink','postgres_fdw')")" == "3" ]] \
  && ok "extensions vector, dblink and postgres_fdw are available" || bad "extension vector, dblink or postgres_fdw is missing"
f=$(q "SELECT failed_count FROM pg_stat_archiver")
[[ "$f" == "0" ]] && ok "WAL archiver has no failures" || bad "WAL archiver reports $f failures (see docker compose logs postgres)"
[[ "$(q "SELECT count(*) FROM pg_roles WHERE rolname='replicator' AND rolreplication")" == "1" ]] \
  && ok "replication role exists (Lesson 2-2 demo)" || bad "role replicator missing: the volume was created by an older image; run docker compose down -v"
grep -q $'\r' /kit/labs/week01/scripts/03_waldump.sh 2>/dev/null \
  && bad "scripts have Windows line endings: see SETUP.md, 'Windows notes'" || ok "scripts have Unix line endings"

echo
echo "Result: $PASS passed, $FAIL failed."
[[ $FAIL -eq 0 ]] && echo "You are ready for Practices 1-4." || exit 1
