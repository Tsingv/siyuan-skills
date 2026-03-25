from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult


class ImportOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def import_std_md(self, notebook: str, local_path: str) -> OperationResult:
        body = self.client.call("/api/import/importStdMd", {"notebook": notebook, "localPath": local_path})
        return OperationResult(
            endpoint="/api/import/importStdMd",
            data=body.get("data"),
            summary=f"已导入 Markdown 文件 {local_path}",
        )
