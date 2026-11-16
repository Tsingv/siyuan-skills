---
name: siyuan
description: This skill should be used when the user asks to "write to SiYuan", "save to SiYuan", "search SiYuan", "query SiYuan notes", "append to an existing SiYuan document", "manage SiYuan notebooks", or needs a local SiYuan Note integration through the bundled Python CLI.
metadata:
  version: 0.1.0
---

# SiYuan Note Skill

Use the bundled Python CLI to interact with a local SiYuan instance instead of sourcing shell functions. Treat this skill as the standard project-level skill entry for SiYuan operations.

## What This Skill Covers

Handle these workflows:
- Health checks and connectivity validation
- Notebook discovery and creation
- Document creation, export, outline, rename, movement, removal, and listing
- Block append/prepend/insert/update/delete/move and batch operations
- SQL queries, block search, tag search, recent block listing, and fulltext search
- Workspace helpers such as `AgentWorkspace`, categorized writes, and smart writes
- Attribute reads/writes and asset uploads
- File access, backlinks, notifications, template rendering, and standard Markdown import
- Flashcards, tags, bookmarks, history queries, graph views, and system inspection

## Primary Entry Point

Run the bundled CLI from the skill directory:

```bash
python3 scripts/siyuan_cli.py <command> ...
```

Examples:

```bash
python3 scripts/siyuan_cli.py health
python3 scripts/siyuan_cli.py notebooks list --format markdown
python3 scripts/siyuan_cli.py query sql --stmt "select * from blocks limit 5"
python3 scripts/siyuan_cli.py workspace smart-write --title "Example" --category "研究笔记" --input-file "/tmp/example.md"
```

Global options such as `--format`, `--host`, and `--timeout` can be placed either before the top-level command or after a subcommand.

## Runtime Model

Follow this order:
1. Run the CLI directly from `scripts/siyuan_cli.py`
2. Let `bootstrap.py` verify Python and install missing dependencies automatically
3. Use structured output by default (`json`)
4. Switch to `markdown` or `csv` only for tabular results that benefit from presentation or export

## Configuration

Read configuration from:
1. CLI flags
2. Environment variables
3. Project `.env`
4. Built-in defaults

Supported inputs:
- `SIYUAN_HOST`
- `SIYUAN_TOKEN`
- `PASSWORD`
- `SIYUAN_TIMEOUT`
- `SIYUAN_OUTPUT_FORMAT`

Default host: `http://127.0.0.1:6806`

## Output Rules

Default to `json` for agent-friendly consumption.

Supported formats:
- `json` — default for reliable downstream consumption
- `markdown` — for readable tables and summaries
- `csv` — for tabular export only
- `text` — for short status output

Apply pandas-based formatting only to tabular record lists such as notebook lists, SQL rows, and search results. Do not force raw markdown documents, outlines, graphs, or nested block trees into DataFrames.

See detailed rules in:
- `references/output-format-spec.md`
- `references/pandas-conversion-guide.md`

## Write Workflow

A supplied document/block ID and an explicit section to edit already specify placement. Resolve its notebook from SiYuan only if needed; proceed with that authorized edit without asking the user to repeat the destination.

Before writing to SiYuan, confirm the target notebook and placement strategy unless the user clearly accepted defaults.

Supported choices:
- Write to `AgentWorkspace`
- Write to a specific notebook by ID or fuzzy-matched name
- Create a new document
- Append or update an existing document/block
- Auto-classify into a workspace category

When no location is specified, prefer:
- notebook: `AgentWorkspace`
- mode: categorized write or smart write

## Layout

This repository keeps the portable skill bundle under `skill/`:
- Standard skill entry: `SKILL.md`
- Main CLI: `scripts/siyuan_cli.py`
- References: `references/`
- Python package: `python/siyuan_skill/`

Use the Python CLI for all new work.

## Focused Reading and Editing

- For a supplied block ID, start with `blocks get-kramdown <id>`. `docs read` is a Markdown **export**, which can resolve to the containing document and expand references into footnotes; use it when exported document content is wanted, not to inspect a local section.
- Locate section headings and their content with `blocks children <id>`. Read only the relevant child subtree with `blocks get-kramdown <child-id>`. Reuse returned IDs and content instead of querying the whole document again.
- For a section replacement, update its content/list block with `blocks update --block-id <id> --input-file <path>`, preserving the section heading and surrounding sections. Read back that changed block once to verify the result. Mutation responses may contain large DOM transaction payloads; `--format text` gives a short status, while JSON preserves the full response.
- For cross-document discovery, select only needed SQL columns and constrain dates, document roots, block types and result count. Container blocks (`l`, `i`) duplicate descendant text; prefer `type IN ('p','h')` for prose searches and `type='d'` for document discovery. `ORDER BY sort` across a whole document does not reconstruct its tree; use child-block traversal for local order.
- For multiple known document roots, batch them into one `root_id IN (...)` SQL query. Retain results for later drafting; repeat reads only for missing information, truncation, or verification after a change.

For weekly reports and other history-based writing, read [references/history-based-editing.md](references/history-based-editing.md).

## Additional Resources

### References
- `references/auth-and-config.md` — auth flow, config precedence, cache behavior
- `references/output-format-spec.md` — standard output envelope and format rules
- `references/pandas-conversion-guide.md` — DataFrame conversion policy and column conventions
- `references/migration-notes.md` — shell-to-Python migration notes and compatibility guidance

### Scripts
- `scripts/bootstrap.py` — dependency checks and auto-install
- `scripts/check_env.py` — runtime inspection
- `scripts/siyuan_cli.py` — main executable entry
