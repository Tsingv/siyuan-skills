# History-based section editing

## Source selection

Separate the source roles: the target block supplies scope, earlier reports supply tone, and records from the requested period supply accomplishments. A previous report's Plan is not evidence that work was completed.

“Historical messages” can mean chat history outside SiYuan. The CLI `history` group accesses SiYuan document history, not Codex/ChatGPT conversations. When conversation tools are available, discover those exact tools separately and read relevant threads; avoid printing an entire unrelated tool catalog. Follow the tool's actual limit and pagination schema. A truncated thread title or summary is only a discovery hint, not evidence of its contents.

Resolve relative dates in the user's timezone. For a Monday weekly report, “last week” ordinarily means the preceding Monday through Sunday. Thread creation date alone does not date every turn; check individual message/turn timestamps where available. Later messages in an older thread may describe work outside the requested period.

## Minimal retrieval sequence

1. Read the supplied block with `blocks get-kramdown`. Inspect children to locate the requested section and its editable content block. Store these IDs.
2. Locate a small number of prior reports, preferably in the same document or known daily-note path. Read enough to establish tone; avoid exporting a reference-heavy document if the relevant blocks are already available.
3. Query records for the requested period in one bounded request. For example, after substituting actual dates:

   ```bash
   python3 scripts/siyuan_cli.py query sql --stmt "SELECT id, root_id, hpath, content, created, updated FROM blocks WHERE type IN ('p','h') AND hpath LIKE '/daily note/2026/11/%' AND created >= '20261109000000' AND created < '20261116000000' ORDER BY created LIMIT 100"
   ```

   `created` limits creation time, not the date of every activity mentioned in the text. Old blocks edited during the week require an `updated` search if relevant. If a result hits its limit, narrow or paginate before treating it as complete.
4. For conversation history, list relevant threads once, then batch independent reads. Read additional pages only when the needed evidence is missing. Do not reread returned content through a second mechanism without a specific gap to resolve.
5. Draft only supported progress, distinguish completed work from ongoing analysis and unverified outcomes, update the target content block, and read it back once.

## Common command shapes

```bash
python3 scripts/siyuan_cli.py blocks get-kramdown <block-id>
python3 scripts/siyuan_cli.py blocks children <heading-id>
python3 scripts/siyuan_cli.py blocks update --block-id <content-block-id> --input-file /tmp/section.md --format text
```

The `--format text` option on structured reads may show only a summary. Keep JSON for `children`, block metadata and kramdown objects when the returned fields are needed.
