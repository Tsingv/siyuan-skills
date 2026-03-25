# Migration Notes

## Current state

The project originally exposed SiYuan operations through repository-level entrypoints.

That approach relied on Bash `source`, `curl`, and `jq`.

## New state

The standard skill entry is now:
- `skill/SKILL.md`

The primary executable path is:
- `skill/scripts/siyuan_cli.py`

## Compatibility guidance

- Use `skill/SKILL.md` and `skill/scripts/siyuan_cli.py` as the supported entrypoints
- Prefer Python CLI for all new implementations
- Use the shell SDK only as a migration reference when an endpoint has not yet been ported

## Why this migration matters

- Better compatibility across agents and environments
- No shell `source` requirement
- Unified output contract
- Standard skill discovery through `SKILL.md`
- Centralized dependency handling and optional auto-install
