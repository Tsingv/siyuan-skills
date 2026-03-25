from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult

DOC_COLUMNS = ["id", "box", "path", "hpath", "content", "updated"]


class DocOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def create_markdown(self, notebook: str, path: str, markdown: str) -> OperationResult:
        body = self.client.call(
            "/api/filetree/createDocWithMd",
            {"notebook": notebook, "path": path, "markdown": markdown},
        )
        return OperationResult(
            endpoint="/api/filetree/createDocWithMd",
            data=body.get("data"),
            summary=f"已创建文档 {path}",
        )

    def rename(self, notebook: str, path: str, title: str) -> OperationResult:
        body = self.client.call(
            "/api/filetree/renameDoc",
            {"notebook": notebook, "path": path, "title": title},
        )
        return OperationResult(
            endpoint="/api/filetree/renameDoc",
            data=body.get("data"),
            summary=f"已重命名文档为 {title}",
        )

    def rename_by_id(self, doc_id: str, title: str) -> OperationResult:
        body = self.client.call("/api/filetree/renameDocByID", {"id": doc_id, "title": title})
        return OperationResult(
            endpoint="/api/filetree/renameDocByID",
            data=body.get("data"),
            summary=f"已重命名文档为 {title}",
        )

    def remove(self, notebook: str, path: str) -> OperationResult:
        body = self.client.call("/api/filetree/removeDoc", {"notebook": notebook, "path": path})
        return OperationResult(
            endpoint="/api/filetree/removeDoc",
            data=body.get("data"),
            summary=f"已删除文档 {path}",
        )

    def remove_by_id(self, doc_id: str) -> OperationResult:
        body = self.client.call("/api/filetree/removeDocByID", {"id": doc_id})
        return OperationResult(
            endpoint="/api/filetree/removeDocByID",
            data=body.get("data"),
            summary=f"已删除文档 {doc_id}",
        )

    def list(self, notebook: str, path: str = "/", sort: int = 0) -> OperationResult:
        body = self.client.call(
            "/api/filetree/listDocsByPath",
            {"notebook": notebook, "path": path, "sort": sort},
        )
        data = body.get("data", [])
        docs = data.get("files") if isinstance(data, dict) else data
        docs = docs or []
        return OperationResult(
            endpoint="/api/filetree/listDocsByPath",
            data=docs,
            tabular=True,
            columns=DOC_COLUMNS,
            summary=f"共 {len(docs)} 个文档",
        )

    def get_hpath_by_id(self, block_id: str) -> OperationResult:
        body = self.client.call("/api/filetree/getHPathByID", {"id": block_id})
        return OperationResult(
            endpoint="/api/filetree/getHPathByID",
            data=body.get("data"),
        )

    def get_path_by_id(self, block_id: str) -> OperationResult:
        body = self.client.call("/api/filetree/getPathByID", {"id": block_id})
        return OperationResult(
            endpoint="/api/filetree/getPathByID",
            data=body.get("data"),
        )

    def get_ids_by_hpath(self, hpath: str, notebook: str) -> OperationResult:
        body = self.client.call("/api/filetree/getIDsByHPath", {"path": hpath, "notebook": notebook})
        return OperationResult(
            endpoint="/api/filetree/getIDsByHPath",
            data=body.get("data"),
            summary="已获取路径对应 ID",
        )

    def move_docs(self, from_paths: list[str], to_notebook: str, to_path: str) -> OperationResult:
        body = self.client.call(
            "/api/filetree/moveDocs",
            {"fromPaths": from_paths, "toNotebook": to_notebook, "toPath": to_path},
        )
        return OperationResult(
            endpoint="/api/filetree/moveDocs",
            data=body.get("data"),
            summary=f"已移动 {len(from_paths)} 个文档",
        )

    def export_markdown(self, doc_id: str) -> OperationResult:
        body = self.client.call("/api/export/exportMdContent", {"id": doc_id})
        return OperationResult(
            endpoint="/api/export/exportMdContent",
            data=body.get("data", {}).get("content", ""),
            summary="已导出 Markdown",
        )

    def read_doc(self, doc_id: str) -> OperationResult:
        return self.export_markdown(doc_id)

    def outline(self, doc_id: str) -> OperationResult:
        body = self.client.call("/api/outline/getDocOutline", {"id": doc_id})
        return OperationResult(
            endpoint="/api/outline/getDocOutline",
            data=body.get("data") or [],
            summary="已获取文档大纲",
        )
