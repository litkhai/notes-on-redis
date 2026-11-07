# STATUS.md

Updated 2026-11-07.

## Tracks

| Track | Run against a real account or container? |
|---|---|
| [`design/`](./design) | n/a — design v0 and two research notes, public pages read 2026-11-07; nothing run |
| `setup/` | Not started |
| `local/` | Not started |
| `cloud/` | Not started — no Redis Cloud account created yet |
| `enterprise/` | Not started |
| `iris/` | Not started |
| `compare/` | Not started |
| `deep-dive/` | Not started |
| [`docs/`](./docs) | Shell only (layout, palette, nav, four-language stub pages); **not deployed** — no Vercel project, no DNS |

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

Listed in [`design/DESIGN.md`](./design/DESIGN.md) §8: Essentials now or later, Pro yes/no,
ElastiCache lab yes/no, Vercel project timing, two or four languages.
