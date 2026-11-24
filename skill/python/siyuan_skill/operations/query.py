from __future__ import annotations

import re
from typing import Sequence

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult

QUERY_COLUMNS = ["id", "root_id", "box", "path", "hpath", "content", "type", "tag", "created", "updated"]
SEARCH_BLOCK_COLUMNS = ["id", "root_id", "box", "path", "hpath", "content", "type", "updated"]
SEARCH_TAG_COLUMNS = ["id", "root_id", "content", "type", "tag", "updated"]
DOC_LIST_COLUMNS = ["id", "box", "path", "hpath", "content", "updated"]
RECENT_BLOCK_COLUMNS = ["id", "root_id", "box", "hpath", "content", "type", "updated"]
PERIOD_ACTIVITY_COLUMNS = ["id", "root_id", "type", "hpath", "content", "created", "updated"]
WEEKLY_HEADING_COLUMNS = ["id", "root_id", "hpath", "content", "created", "updated"]
TAG_API_COLUMNS = ["label", "count"]

_SIYUAN_TS_RE = re.compile(r"^\d{14}$")
_TYPE_RE = re.compile(r"^[a-z]$")


def _sql_quote(value: str) -> str:
    return value.replace("'", "''")


def _require_siyuan_ts(value: str, *, field_name: str) -> str:
    text = value.strip()
    if not _SIYUAN_TS_RE.fullmatch(text):
        raise ValueError(f"{field_name} 需为 14 位 SiYuan 时间戳，例如 20261116000000")
    return text


def _parse_types(types: str | Sequence[str] | None) -> list[str]:
    if types is None:
        raw = ["p", "h"]
    elif isinstance(types, str):
        raw = [part.strip() for part in types.split(",") if part.strip()]
    else:
        raw = [str(part).strip() for part in types if str(part).strip()]
    if not raw:
        raise ValueError("types 不能为空")
    for item in raw:
        if not _TYPE_RE.fullmatch(item):
            raise ValueError(f"非法 block type: {item}")
    return raw


class QueryOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def sql(self, statement: str) -> OperationResult:
        return self._run_sql(statement, columns=None, summary_prefix="SQL")

    def search_blocks(self, keyword: str, limit: int = 20) -> OperationResult:
        safe_keyword = _sql_quote(keyword)
        stmt = (
            "SELECT id, root_id, box, path, hpath, content, type, updated "
            f"FROM blocks WHERE content LIKE '%{safe_keyword}%' "
            f"ORDER BY updated DESC LIMIT {int(limit)}"
        )
        return self._run_sql(stmt, columns=SEARCH_BLOCK_COLUMNS, summary_prefix="搜索")

    def search_by_tag(self, tag: str, limit: int = 20) -> OperationResult:
        safe_tag = _sql_quote(tag)
        stmt = (
            "SELECT id, root_id, content, type, tag, updated "
            f"FROM blocks WHERE tag LIKE '%{safe_tag}%' "
            f"ORDER BY updated DESC LIMIT {int(limit)}"
        )
        return self._run_sql(stmt, columns=SEARCH_TAG_COLUMNS, summary_prefix="标签搜索")

    def search_tag(self, keyword: str) -> OperationResult:
        body = self.client.call("/api/search/searchTag", {"k": keyword})
        data = body.get("data") or []
        return OperationResult(
            endpoint="/api/search/searchTag",
            data=data,
            tabular=isinstance(data, list),
            columns=TAG_API_COLUMNS,
            summary=f"标签联想返回 {len(data) if isinstance(data, list) else 0} 条结果",
        )

    def fulltext_search(self, query: str, page: int = 1) -> OperationResult:
        body = self.client.call("/api/search/fullTextSearchBlock", {"query": query, "page": page})
        data = body.get("data", {})
        blocks = data.get("blocks") if isinstance(data, dict) else data
        if isinstance(blocks, list):
            return OperationResult(
                endpoint="/api/search/fullTextSearchBlock",
                data=blocks,
                tabular=True,
                columns=QUERY_COLUMNS,
                summary=f"全文搜索返回 {len(blocks)} 条结果",
            )
        return OperationResult(
            endpoint="/api/search/fullTextSearchBlock",
            data=data,
            summary="已完成全文搜索",
        )

    def list_all_docs(self, limit: int = 50) -> OperationResult:
        stmt = (
            "SELECT id, box, path, hpath, content, updated "
            f"FROM blocks WHERE type='d' ORDER BY updated DESC LIMIT {int(limit)}"
        )
        return self._run_sql(stmt, columns=DOC_LIST_COLUMNS, summary_prefix="文档列表")

    def recent_blocks(self, limit: int = 20) -> OperationResult:
        stmt = (
            "SELECT id, root_id, box, hpath, content, type, updated "
            f"FROM blocks ORDER BY updated DESC LIMIT {int(limit)}"
        )
        return self._run_sql(stmt, columns=RECENT_BLOCK_COLUMNS, summary_prefix="最近更新")

    def period_activity(
        self,
        start: str,
        end: str,
        *,
        types: str | Sequence[str] | None = "p,h",
        keyword: Sequence[str] | str | None = None,
        hpath_like: Sequence[str] | str | None = None,
        preview_chars: int = 240,
        limit: int = 100,
        before_updated: str | None = None,
    ) -> OperationResult:
        """List blocks created or updated in [start, end).

        Covers project notes as well as daily notes. ``preview_chars>0`` uses
        ``substr(content, ...)`` for discovery; full text still needs get-kramdown.
        """
        start_ts = _require_siyuan_ts(start, field_name="start")
        end_ts = _require_siyuan_ts(end, field_name="end")
        if start_ts >= end_ts:
            raise ValueError("start 必须早于 end")
        type_list = _parse_types(types)
        limit_n = max(1, int(limit))
        preview_n = max(0, int(preview_chars))

        content_expr = (
            f"substr(content,1,{preview_n}) AS content" if preview_n > 0 else "content"
        )
        type_sql = ", ".join(f"'{item}'" for item in type_list)
        where = [
            f"type IN ({type_sql})",
            (
                f"((created >= '{start_ts}' AND created < '{end_ts}') "
                f"OR (updated >= '{start_ts}' AND updated < '{end_ts}'))"
            ),
        ]

        keywords = _as_str_list(keyword)
        hpaths = _as_str_list(hpath_like)
        filter_parts: list[str] = []
        for item in keywords:
            safe = _sql_quote(item)
            filter_parts.append(f"content LIKE '%{safe}%'")
        for item in hpaths:
            safe = _sql_quote(item)
            filter_parts.append(f"hpath LIKE '%{safe}%'")
        if filter_parts:
            where.append("(" + " OR ".join(filter_parts) + ")")

        if before_updated:
            before_ts = _require_siyuan_ts(before_updated, field_name="before_updated")
            where.append(f"updated < '{before_ts}'")

        stmt = (
            f"SELECT id, root_id, type, hpath, {content_expr}, created, updated "
            f"FROM blocks WHERE {' AND '.join(where)} "
            f"ORDER BY updated DESC LIMIT {limit_n}"
        )
        result = self._run_sql(stmt, columns=PERIOD_ACTIVITY_COLUMNS, summary_prefix="时段活动")
        row_count = len(result.data) if isinstance(result.data, list) else 0
        result.meta.update(
            {
                "start": start_ts,
                "end": end_ts,
                "types": type_list,
                "preview_chars": preview_n,
                "limit": limit_n,
                "truncated": row_count >= limit_n,
                "keywords": keywords,
                "hpath_like": hpaths,
            }
        )
        if row_count >= limit_n:
            result.summary = (
                f"{result.summary}（可能截断；请收窄条件或用 --before-updated 翻页）"
            )
        return result

    def weekly_headings(self, title_like: str = "周报", limit: int = 15) -> OperationResult:
        safe = _sql_quote(title_like)
        limit_n = max(1, int(limit))
        stmt = (
            "SELECT id, root_id, hpath, content, created, updated FROM blocks "
            f"WHERE type='h' AND content LIKE '%{safe}%' "
            f"ORDER BY updated DESC LIMIT {limit_n}"
        )
        return self._run_sql(stmt, columns=WEEKLY_HEADING_COLUMNS, summary_prefix="周报标题")

    def _run_sql(self, statement: str, *, columns: list[str] | None, summary_prefix: str) -> OperationResult:
        body = self.client.call("/api/query/sql", {"stmt": statement})
        rows = body.get("data", [])
        row_count = len(rows) if isinstance(rows, list) else 0
        if columns is None and isinstance(rows, list):
            columns = list(dict.fromkeys(key for row in rows if isinstance(row, dict) for key in row))
        return OperationResult(
            endpoint="/api/query/sql",
            data=rows,
            tabular=isinstance(rows, list),
            columns=columns,
            summary=f"{summary_prefix}返回 {row_count} 行",
        )


def _as_str_list(value: Sequence[str] | str | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    return [str(item) for item in value if str(item)]
