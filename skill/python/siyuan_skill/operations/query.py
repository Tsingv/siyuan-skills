from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult

QUERY_COLUMNS = ["id", "root_id", "box", "path", "hpath", "content", "type", "tag", "created", "updated"]
SEARCH_BLOCK_COLUMNS = ["id", "root_id", "box", "path", "hpath", "content", "type", "updated"]
SEARCH_TAG_COLUMNS = ["id", "root_id", "content", "type", "tag", "updated"]
DOC_LIST_COLUMNS = ["id", "box", "path", "hpath", "content", "updated"]
RECENT_BLOCK_COLUMNS = ["id", "root_id", "box", "hpath", "content", "type", "updated"]
TAG_API_COLUMNS = ["label", "count"]


class QueryOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def sql(self, statement: str) -> OperationResult:
        return self._run_sql(statement, columns=QUERY_COLUMNS, summary_prefix="SQL")

    def search_blocks(self, keyword: str, limit: int = 20) -> OperationResult:
        safe_keyword = keyword.replace("'", "''")
        stmt = (
            "SELECT id, root_id, box, path, hpath, content, type, updated "
            f"FROM blocks WHERE content LIKE '%{safe_keyword}%' "
            f"ORDER BY updated DESC LIMIT {int(limit)}"
        )
        return self._run_sql(stmt, columns=SEARCH_BLOCK_COLUMNS, summary_prefix="搜索")

    def search_by_tag(self, tag: str, limit: int = 20) -> OperationResult:
        safe_tag = tag.replace("'", "''")
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

    def _run_sql(self, statement: str, *, columns: list[str] | None, summary_prefix: str) -> OperationResult:
        body = self.client.call("/api/query/sql", {"stmt": statement})
        rows = body.get("data", [])
        row_count = len(rows) if isinstance(rows, list) else 0
        return OperationResult(
            endpoint="/api/query/sql",
            data=rows,
            tabular=isinstance(rows, list),
            columns=columns,
            summary=f"{summary_prefix}返回 {row_count} 行",
        )
