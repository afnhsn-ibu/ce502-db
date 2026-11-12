# Recovery Runbook · `shop` database · accidental data loss

> A runbook is written **before** the incident, for a colleague who must act alone under stress. Use numbered steps, exact commands and a clear check after every step. 5–8 steps.

| Field | Value |
|---|---|
| System | `shop` on container `ce502-postgres` |
| Scenario covered | *e.g. rows deleted or a table dropped by mistake* |
| Backups available | *e.g. nightly `pg_dump -Fc` in /backup; base backup + WAL archive in /backup/base, /archive* |
| Target RTO / RPO | |
| Owner and escalation contact | |
| Last tested | *date, by whom, measured time* |

## Steps

| # | Action (exact command or decision) | Check before moving on | Time |
|---|---|---|---|
| 1 | *e.g. Stop the damage: put the application in maintenance mode / revoke write access* | | |
| 2 | *e.g. Record what happened and when: time of the mistake, what was affected* | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |

## After the incident

- *Who must be informed?*
- *What is written in the incident log?*
- *What change prevents this from happening again?*
