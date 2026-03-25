# Pandas Conversion Guide

## When to use pandas

Use pandas only for homogeneous record lists such as:
- notebook lists
- SQL results
- search results
- recent block lists
- document lists

Do not use pandas for:
- markdown document bodies
- block trees
- graph payloads
- outline trees
- binary or upload responses

## Input contract

Input must be `list[dict]`.
If the list is empty, emit an empty DataFrame with the configured columns when possible.

## Normalization rules

- Replace `None` with empty string
- Keep booleans and numbers as-is
- Convert nested dict/list values to JSON strings
- Truncate long cell values to keep markdown tables readable
- Fill missing columns with empty string

## Standard column order

### Notebook lists
- `id`
- `name`
- `icon`
- `sort`
- `closed`

### Common block/query results
- `id`
- `root_id`
- `box`
- `path`
- `hpath`
- `content`
- `type`
- `tag`
- `created`
- `updated`

## Markdown rendering rules

- Show first 50 rows by default
- Add summary lines for endpoint and row count
- Avoid wide raw JSON blobs in table cells

## CSV rendering rules

- UTF-8 encoding
- Header row required
- Preserve original scalar values where possible
