---
name: redis-free-plan-check
description: Decide whether a workload fits the Redis Cloud free plan (30 MB, 30 connections, no TLS) from the user's stated data size, connection count and security needs, and say which limit it breaks. Do not use for pricing of paid plans.
---
1. Collect three facts from the user: data size, peak client connections, and whether traffic must be encrypted. Ask for any that is missing.
2. Read references/limits.md for the measured limits and what happens at each one.
3. Compare each fact with its limit. A workload fits only if all three fit.
4. Answer with "fits" or "does not fit", then one line per limit that is broken, using the behaviour from references/limits.md.
Do not quote paid-plan prices. Do not promise throughput: the 100 ops/s on the pricing page was not enforced in the measurement.
