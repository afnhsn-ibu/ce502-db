# Practice 4 · Part C · Autonomy, Distribution, Heterogeneity (A/D/H) Worksheet

Place each system on the three dimensions from Özsu & Valduriez:

- **Autonomy:** A0 tight integration · A1 semi-autonomous · A2 total isolation (fully autonomous)
- **Distribution:** D0 not distributed · D1 client–server · D2 peer-to-peer (fully distributed)
- **Heterogeneity:** H0 homogeneous · H1 heterogeneous

For each system give (A, D, H) and one sentence of justification. There can be more than one defensible answer; the justification is what earns the marks.

| # | System | A | D | H | Justification |
|---|---|---|---|---|---|
| 1 | A single PostgreSQL server used by a web application | | | | |
| 2 | Our `ddb_global` lab setup (two PostgreSQL sites behind postgres_fdw) | | | | |
| 3 | PostgreSQL + Citus, one table sharded over 4 worker nodes | | | | |
| 4 | A MongoDB sharded cluster | | | | |
| 5 | Apache Cassandra with 6 peer nodes in 2 data centres | | | | |
| 6 | Trino querying a MySQL sales database, a PostgreSQL HR database and Parquet files in S3 | | | | |
| 7 | A university that links its existing library system (Oracle) and student system (SQL Server) through a federated view layer, without changing either system | | | | |
| 8 | Google Spanner | | | | |
