# History-based section editing

## Source selection

Separate the source roles: the target block supplies scope, earlier reports supply tone, and records from the requested period supply accomplishments. A previous report's Plan is not evidence that work was completed. Mirror the tone of prior reports; do not invent a template voice or auto-generate a report from keywords alone. Period-activity SQL is for evidence gathering only—there is no fully automatic weekly-report generation in this skill.

“Historical messages” can mean chat history outside SiYuan. The CLI `history` group accesses SiYuan document history, not Codex/ChatGPT conversations. When conversation tools are available, discover those exact tools separately and read relevant threads; avoid printing an entire unrelated tool catalog. Follow the tool's actual limit and pagination schema. A truncated thread title or summary is only a discovery hint, not evidence of its contents.

Resolve relative dates in the user's timezone. For a Monday weekly report, “last week” ordinarily means the preceding Monday through Sunday. Thread creation date alone does not date every turn; check individual message/turn timestamps where available. Later messages in an older thread may describe work outside the requested period.

Evidence for weekly reports often lives outside daily notes (project notes, vulnerability drafts, research docs). Do not treat `/daily note/...` as the only source path.

## Read-only / bootstrap caution

`scripts/siyuan_cli.py` runs `bootstrap.py` on startup and may `pip install` missing deps. In workflow stages that forbid mutation, prefer HTTP GET/`fetch` against the SiYuan API with an existing token, or use an already-installed environment. Do not rely on first-time CLI bootstrap during locked phases.

## Minimal retrieval sequence

1. Read the supplied block with `blocks get-kramdown`. For a weekly-report heading, that often returns only the heading line; use `blocks children <heading-or-doc-id>` to locate section headings (`Target`, `Outlined Achievements`, `Achievements`, `Plan`, …) and the editable list/content block under each. Store those content-block IDs.
2. Locate a small number of prior reports for tone (see “Prior weekly reports” below). Read their section list blocks with `blocks children` / `blocks get-kramdown` on the content blocks; avoid exporting a reference-heavy document if the relevant blocks are already available.
3. Query period activity across notebooks (see “Period evidence query”). Prefer one bounded request that uses `created` **or** `updated`, not daily-note-only filters.
4. Run a second, Target-aligned keyword query (see “Target keyword second pass”) so side projects unrelated to this week’s Target are not treated as achievements.
5. If SQL used `substr`, markdown tables truncated cells, or any preview looks incomplete, call `blocks get-kramdown <id>` (JSON) on each candidate before drafting. Truncated SQL/markdown is discovery only, not draft evidence.
6. For conversation history, list relevant threads once, then batch independent reads. Read additional pages only when the needed evidence is missing. Do not reread returned content through a second mechanism without a specific gap to resolve.
7. Draft only supported progress; distinguish completed work from ongoing analysis and unverified outcomes. Update each section’s content/list block separately, then read that same block back once.

## Prior weekly reports

Prefer the dedicated helper (adjust `--title-like` if needed):

```bash
python3 scripts/siyuan_cli.py query weekly-headings --title-like 周报 --limit 15
```

Then `blocks children <heading-id>` on the latest completed report(s) and read Achievements/Plan list blocks for tone. Prefer same notebook / daily-note tree when available.

## Period evidence query

Use `query period-activity` instead of hand-written SQL. It queries **created OR updated** in `[--start, --end)`, defaults to types `p,h`, returns stable columns, and is **not** limited to `/daily note/...`. This gathers evidence only—it does not auto-write the weekly report.

Timestamps are 14-digit SiYuan times (e.g. `20261116000000`).

Discovery pass (content preview truncated by default):

```bash
python3 scripts/siyuan_cli.py query period-activity \
  --start 20261116000000 --end 20261123000000 \
  --limit 100
```

Documents touched in the window:

```bash
python3 scripts/siyuan_cli.py query period-activity \
  --start 20261116000000 --end 20261123000000 \
  --types d --preview-chars 0 --limit 50
```

If `meta.truncated` is true (or `row_count == limit`), narrow with `--keyword` / `--hpath-like`, raise `--limit`, or paginate with `--before-updated <last_seen_updated>`.

## Target keyword second pass

After reading this week’s `Target` list, filter the same window with Target terms / project paths:

```bash
python3 scripts/siyuan_cli.py query period-activity \
  --start 20261116000000 --end 20261123000000 \
  --keyword Passkey --keyword XR --keyword 漏洞 --keyword Artifacts \
  --hpath-like SP27 --hpath-like Passkey \
  --limit 80
```

Repeated `--keyword` / `--hpath-like` values are OR-combined. Edits that never match Target stay out of Achievements unless the user asked to include them.

## Truncation → full read

- SQL `substr(...)`, CLI markdown table cell clipping, and `--format text` summaries are incomplete.
- Before drafting from a block, `blocks get-kramdown <id> --format json` (or `blocks children` on a heading that owns the prose).
- If kramdown still looks cut off in the DOM preview, use `blocks get-dom` only as a fallback; prefer kramdown for edit fidelity.

## Multi-section weekly report write-back

Weekly reports usually have several editable list blocks under one heading. Do not replace the whole H1 in one shot unless the user asked for a full rewrite.

1. `blocks children` on the weekly-report heading (or doc) → map each H2 to its following list/content block id.
2. Leave filled sections (e.g. `Target`) unchanged unless asked.
3. For each section to fill (`Outlined Achievements`, `Achievements`, `Plan`, …), `blocks update --block-id <content-block-id> --input-file /tmp/<section>.md --format text`.
4. After each update (or once per changed id), `blocks get-kramdown <content-block-id>` to verify that section only.

## Common command shapes

```bash
python3 scripts/siyuan_cli.py blocks get-kramdown <block-id>
python3 scripts/siyuan_cli.py blocks children <heading-id>
python3 scripts/siyuan_cli.py blocks update --block-id <content-block-id> --input-file /tmp/section.md --format text
```

The `--format text` option on structured reads may show only a summary. Keep JSON for `children`, block metadata and kramdown objects when the returned fields are needed.
