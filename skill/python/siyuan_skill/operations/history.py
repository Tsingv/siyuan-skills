from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult


class HistoryOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def get_doc_history(self, history_path: str) -> OperationResult:
        body = self.client.call("/api/history/getDocHistoryContent", {"historyPath": history_path})
        return OperationResult(
            endpoint="/api/history/getDocHistoryContent",
            data=body.get("data"),
            summary="已获取历史内容",
        )

    def search_history(self, query: str, page: int = 1, history_type: int = 0) -> OperationResult:
        body = self.client.call(
            "/api/history/searchHistory",
            {"query": query, "page": page, "type": history_type},
        )
        data = body.get("data", {})
        return OperationResult(
            endpoint="/api/history/searchHistory",
            data=data,
            summary="已搜索历史记录",
        )
