# Output Format Specification

## Standard envelope

All `json` responses should follow this structure:

```json
{
  "ok": true,
  "endpoint": "/api/notebook/lsNotebooks",
  "data": [],
  "meta": {
    "format": "json",
    "tabular": true,
    "row_count": 0,
    "columns": ["id", "name"]
  }
}
```

## Formats

### json
- Default for agent consumption
- Preserve structured data
- Include `endpoint` and `meta`

### markdown
- Use for tabular presentation
- Limit displayed rows to 50 by default
- Include endpoint and row count summary above the table

### csv
- Only for tabular record lists
- UTF-8, header row included
- Reject non-tabular data

### text
- Use for short status summaries
- Prefer one-line or short paragraph output

## Tabular policy

Treat data as tabular only when it is a homogeneous `list[dict]`.
Do not force these into tables:
- raw markdown documents
- nested outlines
- graphs
- arbitrary nested JSON
