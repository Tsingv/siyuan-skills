from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult

BOOKMARK_COLUMNS = ["name", "url", "icon"]


class BookmarkOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def get_bookmarks(self) -> OperationResult:
        body = self.client.call("/api/bookmark/getBookmark", {})
        data = body.get("data") or []
        return OperationResult(
            endpoint="/api/bookmark/getBookmark",
            data=data,
            tabular=isinstance(data, list),
            columns=BOOKMARK_COLUMNS,
            summary=f"共 {len(data) if isinstance(data, list) else 0} 个书签",
        )
