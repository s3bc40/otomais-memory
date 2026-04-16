# Git Conventions

## Commit style

- Use [Conventional Commits](https://www.conventionalcommits.org/): `type: description`
- Common types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`
- Keep the subject line under 72 characters, imperative mood ("add" not "added")

## Atomic commits

- One logical concern per commit — never bundle unrelated changes
- Typical split for a feature: model → migration → views → urls → tests
- Typical split for project setup: tooling → framework scaffold → dev context → docs

## What not to commit

- `db.sqlite3` and any `*.sqlite3` files
- `.env` and `.env.local`
- `.claude/settings.local.json`
- `__pycache__/` and `*.pyc`
