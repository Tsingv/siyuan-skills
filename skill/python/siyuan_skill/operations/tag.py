from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult

TAG_COLUMNS = ["label", "count"]


class TagOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def get_tags(self) -> OperationResult:
        body = self.client.call("/api/tag/getTag", {})
        data = body.get("data") or []
        return OperationResult(
            endpoint="/api/tag/getTag",
            data=data,
            tabular=isinstance(data, list),
            columns=TAG_COLUMNS,
            summary=f"共 {len(data) if isinstance(data, list) else 0} 个标签",
        )

    def rename_tag(self, old_label: str, new_label: str) -> OperationResult:
        body = self.client.call("/api/tag/renameTag", {"oldLabel": old_label, "newLabel": new_label})
        return OperationResult(
            endpoint="/api/tag/renameTag",
            data=body.get("data"),
            summary=f"已将标签 {old_label} 重命名为 {new_label}",
        )
