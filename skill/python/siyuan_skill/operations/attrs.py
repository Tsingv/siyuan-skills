from __future__ import annotations

from typing import Any

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult


class AttrOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def get(self, block_id: str) -> OperationResult:
        body = self.client.call("/api/attr/getBlockAttrs", {"id": block_id})
        return OperationResult(
            endpoint="/api/attr/getBlockAttrs",
            data=body.get("data", {}),
            summary="已获取块属性",
        )

    def set(self, block_id: str, attrs: dict[str, Any]) -> OperationResult:
        body = self.client.call("/api/attr/setBlockAttrs", {"id": block_id, "attrs": attrs})
        return OperationResult(
            endpoint="/api/attr/setBlockAttrs",
            data=body.get("data"),
            summary="已设置块属性",
        )
