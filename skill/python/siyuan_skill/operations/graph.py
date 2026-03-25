from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult


class GraphOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def get_graph(self) -> OperationResult:
        body = self.client.call(
            "/api/graph/getGraph",
            {"k": "", "conf": {"minRefs": 0, "dailyNote": False}},
        )
        return OperationResult(
            endpoint="/api/graph/getGraph",
            data=body.get("data"),
            summary="已获取全局图谱",
        )

    def get_local_graph(self, block_id: str) -> OperationResult:
        body = self.client.call(
            "/api/graph/getLocalGraph",
            {"id": block_id, "k": "", "conf": {"minRefs": 0, "dailyNote": False}},
        )
        return OperationResult(
            endpoint="/api/graph/getLocalGraph",
            data=body.get("data"),
            summary="已获取局部图谱",
        )
