from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult


class FileOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def get_file(self, path: str) -> OperationResult:
        body = self.client.call("/api/file/getFile", {"path": path})
        return OperationResult(
            endpoint="/api/file/getFile",
            data=body.get("data"),
            summary=f"已读取文件 {path}",
        )

    def read_dir(self, path: str) -> OperationResult:
        body = self.client.call("/api/file/readDir", {"path": path})
        data = body.get("data") or []
        return OperationResult(
            endpoint="/api/file/readDir",
            data=data,
            tabular=isinstance(data, list),
            summary=f"已读取目录 {path}",
        )

    def remove_file(self, path: str) -> OperationResult:
        body = self.client.call("/api/file/removeFile", {"path": path})
        return OperationResult(
            endpoint="/api/file/removeFile",
            data=body.get("data"),
            summary=f"已删除文件 {path}",
        )
