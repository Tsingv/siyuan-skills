from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult


class RefOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def backlinks(self, block_id: str, sort: str = "3", m_sort: str = "3") -> OperationResult:
        body = self.client.call(
            "/api/ref/getBacklink2",
            {"id": block_id, "sort": sort, "mSort": m_sort},
        )
        return OperationResult(
            endpoint="/api/ref/getBacklink2",
            data=body.get("data"),
            summary="已获取反向链接",
        )
