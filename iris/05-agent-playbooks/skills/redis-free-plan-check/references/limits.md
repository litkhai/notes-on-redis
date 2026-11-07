Redis Cloud free plan, measured 2026-11-07 on this site (cloud/01-free-database):
- Memory: 30 MB. Writes are refused at about 28 MB of values with "OOM command not allowed"; with volatile-lru and no TTLs nothing is evicted.
- Connections: 30. Connection 31 is refused with "max number of clients reached". Iris services on the same database hold their own connections.
- TLS: not available on the free plan; the REST API refuses enableTls.
