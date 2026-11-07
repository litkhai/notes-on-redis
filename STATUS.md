# STATUS.md

Updated 2026-11-07.

## Tracks

| Track | Run against a real account or container? |
|---|---|
| [`design/`](./design) | n/a — design v0 and two research notes, public pages read 2026-11-07; nothing run |
| `setup/` | Not started — [#2](https://github.com/litkhai/redis-hols/issues/2) |
| `local/` | Not started — [#2](https://github.com/litkhai/redis-hols/issues/2) |
| `cloud/` | Not started — no Redis Cloud account yet; [#4](https://github.com/litkhai/redis-hols/issues/4), [#8](https://github.com/litkhai/redis-hols/issues/8) budget, [#12](https://github.com/litkhai/redis-hols/issues/12) budget |
| `enterprise/` | Not started — [#9](https://github.com/litkhai/redis-hols/issues/9) |
| `iris/` | Not started — [#3](https://github.com/litkhai/redis-hols/issues/3), [#7](https://github.com/litkhai/redis-hols/issues/7), [#11](https://github.com/litkhai/redis-hols/issues/11) |
| `compare/` | Not started — [#5](https://github.com/litkhai/redis-hols/issues/5), [#12](https://github.com/litkhai/redis-hols/issues/12) budget |
| `deep-dive/` | Not started — [#6](https://github.com/litkhai/redis-hols/issues/6), [#10](https://github.com/litkhai/redis-hols/issues/10) |
| [`docs/`](./docs) | Shell only (layout, palette, nav, four-language stub pages); **not deployed** — no Vercel project, no DNS; [#13](https://github.com/litkhai/redis-hols/issues/13) |

## CI

`checks` on pull requests: `docs` (`scripts/check-docs.py`), `syntax`, `secrets`
(gitleaks with `.gitleaks.toml`, full history), `hygiene`. The same checks run on staged
files in `.githooks/pre-commit` — enable once per clone with `git config core.hooksPath .githooks`.
`pages.yml` is not added until the Vercel host exists.

## Budget spent

| Date | What | Amount |
|---|---|---|
| — | nothing yet | $0 |

## Open decisions

[`design/DESIGN.md`](./design/DESIGN.md) §8 — Essentials now or later ([#8](https://github.com/litkhai/redis-hols/issues/8)), Pro and ElastiCache ([#12](https://github.com/litkhai/redis-hols/issues/12)), Vercel timing ([#13](https://github.com/litkhai/redis-hols/issues/13)), two or four languages ([#14](https://github.com/litkhai/redis-hols/issues/14)). Skeleton with every lab directory: [#1](https://github.com/litkhai/redis-hols/issues/1).

How an agent picks up an issue: [`design/AGENT-GUIDE.md`](./design/AGENT-GUIDE.md).
