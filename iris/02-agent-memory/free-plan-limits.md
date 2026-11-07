# Redis Cloud free plan: what this site measured (2026-11-07)

The free plan gives one database of 30 MB in a region you choose. The 31st connection is refused
with "max number of clients reached", so the plan allows 30 connections. Writes stop with an OOM
error at about 28 MB of values. The plan advertises 100 operations per second, but that was not
enforced: about 104,000 operations per second ran for 60 seconds without errors. TLS cannot be
turned on for a free database; the API refuses enableTls. The free plan has no replication, no
persistence and no backups. Essentials starts at $5 a month and Pro at $200 a month.
