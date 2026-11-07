# STATUS.md

## Tracks

| Track | Run against a real account or container? |
|---|---|
| [`design/`](./design) | n/a — design v0 and two research notes, public pages read 2026-11-07; nothing run |
| `setup/` | Not started — [#2](https://github.com/litkhai/notes-on-redis/issues/2) |
| `local/` | Not started — [#2](https://github.com/litkhai/notes-on-redis/issues/2) |
| `cloud/` | `01` free database run 2026-11-07 (Redis 8.6.2, Seoul): connection and memory limits enforced, 100 ops/s not; `02` console walkthrough captured (31 screens, masked). Free database `notes-on-redis-free` kept for Iris; API user key `notes-on-redis-lab` exists ([#17](https://github.com/litkhai/notes-on-redis/issues/17)). Open: [#8](https://github.com/litkhai/notes-on-redis/issues/8) budget, [#12](https://github.com/litkhai/notes-on-redis/issues/12) budget, [#17](https://github.com/litkhai/notes-on-redis/issues/17) |
| `enterprise/` | Not started — [#9](https://github.com/litkhai/notes-on-redis/issues/9) |
| `iris/` | Not started — [#3](https://github.com/litkhai/notes-on-redis/issues/3), [#7](https://github.com/litkhai/notes-on-redis/issues/7), [#11](https://github.com/litkhai/notes-on-redis/issues/11) |
| `compare/` | `02` ElastiCache Serverless for Valkey run 2026-11-07 (Valkey 9.0, Seoul, Public + IAM): created, probed with the `cloud/01` script, deleted after ~31 min; console walkthrough captured (12 screens). `01` and the matrix not started — [#5](https://github.com/litkhai/notes-on-redis/issues/5) |
| `deep-dive/` | Not started — [#6](https://github.com/litkhai/notes-on-redis/issues/6), [#10](https://github.com/litkhai/notes-on-redis/issues/10) |
| [`docs/`](./docs) | Live at https://redis.litkhai.dev (Vercel, deploys on push to `main`); seven languages (#22); `/cloud/` and the ElastiCache part of `/compare/` have content, the rest are stubs. Pages redirect stubs not added yet: [#13](https://github.com/litkhai/notes-on-redis/issues/13) |

## CI

`checks` on pull requests: `docs` (`scripts/check-docs.py`), `syntax`, `secrets`
(gitleaks with `.gitleaks.toml`, full history), `hygiene`. The same checks run on staged
files in `.githooks/pre-commit` — enable once per clone with `git config core.hooksPath .githooks`.
`pages.yml` is not added until the Vercel host exists.

## Budget spent

| Date | What | Amount |
|---|---|---|
| 2026-11-07 | Redis Cloud free database, Seoul (`cloud/01`, `cloud/02`) | $0 |
| 2026-11-07 | ElastiCache Serverless for Valkey, Seoul, ~31 min (`compare/02`) | ≈ $0.05 by the price list; billed amount not visible yet |

## Open decisions

[`design/DESIGN.md`](./design/DESIGN.md) §8 — Essentials now or later ([#8](https://github.com/litkhai/notes-on-redis/issues/8)), Pro and ElastiCache ([#12](https://github.com/litkhai/notes-on-redis/issues/12)), Vercel timing ([#13](https://github.com/litkhai/notes-on-redis/issues/13)), Skeleton with every lab directory: [#1](https://github.com/litkhai/notes-on-redis/issues/1).

How an agent picks up an issue: [`design/AGENT-GUIDE.md`](./design/AGENT-GUIDE.md).
