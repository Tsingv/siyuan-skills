from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult


class BlockOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def append(self, markdown: str, parent_id: str) -> OperationResult:
        body = self.client.call(
            "/api/block/appendBlock",
            {"dataType": "markdown", "data": markdown, "parentID": parent_id},
        )
        return OperationResult(
            endpoint="/api/block/appendBlock",
            data=body.get("data"),
            summary=f"已追加到块 {parent_id}",
        )

    def prepend(self, markdown: str, parent_id: str) -> OperationResult:
        body = self.client.call(
            "/api/block/prependBlock",
            {"dataType": "markdown", "data": markdown, "parentID": parent_id},
        )
        return OperationResult(
            endpoint="/api/block/prependBlock",
            data=body.get("data"),
            summary=f"已插入到块 {parent_id} 开头",
        )

    def insert_after(self, markdown: str, previous_id: str) -> OperationResult:
        body = self.client.call(
            "/api/block/insertBlock",
            {"dataType": "markdown", "data": markdown, "previousID": previous_id},
        )
        return OperationResult(
            endpoint="/api/block/insertBlock",
            data=body.get("data"),
            summary=f"已在块 {previous_id} 后插入",
        )

    def update(self, markdown: str, block_id: str) -> OperationResult:
        body = self.client.call(
            "/api/block/updateBlock",
            {"dataType": "markdown", "data": markdown, "id": block_id},
        )
        return OperationResult(
            endpoint="/api/block/updateBlock",
            data=body.get("data"),
            summary=f"已更新块 {block_id}",
        )

    def delete(self, block_id: str) -> OperationResult:
        body = self.client.call("/api/block/deleteBlock", {"id": block_id})
        return OperationResult(
            endpoint="/api/block/deleteBlock",
            data=body.get("data"),
            summary=f"已删除块 {block_id}",
        )

    def move(self, block_id: str, previous_id: str | None = None, parent_id: str | None = None) -> OperationResult:
        payload: dict[str, Any] = {"id": block_id}
        if previous_id:
            payload["previousID"] = previous_id
        if parent_id:
            payload["parentID"] = parent_id
        body = self.client.call("/api/block/moveBlock", payload)
        return OperationResult(
            endpoint="/api/block/moveBlock",
            data=body.get("data"),
            summary=f"已移动块 {block_id}",
        )

    def get_info(self, block_id: str) -> OperationResult:
        body = self.client.call("/api/block/getBlockInfo", {"id": block_id})
        return OperationResult(
            endpoint="/api/block/getBlockInfo",
            data=body.get("data"),
            summary="已获取块信息",
        )

    def get_kramdown(self, block_id: str) -> OperationResult:
        body = self.client.call("/api/block/getBlockKramdown", {"id": block_id})
        return OperationResult(
            endpoint="/api/block/getBlockKramdown",
            data=body.get("data"),
            summary="已获取块内容",
        )

    def get_dom(self, block_id: str) -> OperationResult:
        body = self.client.call("/api/block/getBlockDOM", {"id": block_id})
        return OperationResult(
            endpoint="/api/block/getBlockDOM",
            data=body.get("data"),
            summary="已获取块 DOM",
        )

    def children(self, block_id: str) -> OperationResult:
        body = self.client.call("/api/block/getChildBlocks", {"id": block_id})
        return OperationResult(
            endpoint="/api/block/getChildBlocks",
            data=body.get("data") or [],
            summary="已获取子块",
        )

    def fold(self, block_id: str) -> OperationResult:
        body = self.client.call("/api/block/foldBlock", {"id": block_id})
        return OperationResult(
            endpoint="/api/block/foldBlock",
            data=body.get("data"),
            summary=f"已折叠块 {block_id}",
        )

    def unfold(self, block_id: str) -> OperationResult:
        body = self.client.call("/api/block/unfoldBlock", {"id": block_id})
        return OperationResult(
            endpoint="/api/block/unfoldBlock",
            data=body.get("data"),
            summary=f"已展开块 {block_id}",
        )

    def batch_append(self, parent_id: str, datas: Sequence[str]) -> OperationResult:
        body = self.client.call(
            "/api/block/batchAppendBlock",
            {"parentID": parent_id, "dataType": "markdown", "datas": list(datas)},
        )
        return OperationResult(
            endpoint="/api/block/batchAppendBlock",
            data=body.get("data"),
            summary=f"已批量追加 {len(datas)} 个块",
        )

    def batch_update(self, blocks: list[dict[str, Any]]) -> OperationResult:
        body = self.client.call("/api/block/batchUpdateBlock", {"blocks": blocks})
        return OperationResult(
            endpoint="/api/block/batchUpdateBlock",
            data=body.get("data"),
            summary=f"已批量更新 {len(blocks)} 个块",
        )
