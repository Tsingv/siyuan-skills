from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult

NOTEBOOK_COLUMNS = ["id", "name", "icon", "sort", "closed"]


class NotebookOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def list(self) -> OperationResult:
        body = self.client.call("/api/notebook/lsNotebooks", {})
        notebooks = body.get("data", {}).get("notebooks", [])
        return OperationResult(
            endpoint="/api/notebook/lsNotebooks",
            data=notebooks,
            tabular=True,
            columns=NOTEBOOK_COLUMNS,
            summary=f"共 {len(notebooks)} 个笔记本",
        )

    def create(self, name: str) -> OperationResult:
        body = self.client.call("/api/notebook/createNotebook", {"name": name})
        data = body.get("data")
        if isinstance(data, dict):
            notebook = data.get("notebook") or data
        else:
            notebook = {"id": data, "name": name} if data else {"name": name}
        return OperationResult(
            endpoint="/api/notebook/createNotebook",
            data=notebook,
            summary=f"已创建笔记本 {name}",
        )

    def open(self, notebook_id: str) -> OperationResult:
        body = self.client.call("/api/notebook/openNotebook", {"notebook": notebook_id})
        return OperationResult(
            endpoint="/api/notebook/openNotebook",
            data=body.get("data"),
            summary=f"已打开笔记本 {notebook_id}",
        )

    def close(self, notebook_id: str) -> OperationResult:
        body = self.client.call("/api/notebook/closeNotebook", {"notebook": notebook_id})
        return OperationResult(
            endpoint="/api/notebook/closeNotebook",
            data=body.get("data"),
            summary=f"已关闭笔记本 {notebook_id}",
        )

    def rename(self, notebook_id: str, name: str) -> OperationResult:
        body = self.client.call("/api/notebook/renameNotebook", {"notebook": notebook_id, "name": name})
        return OperationResult(
            endpoint="/api/notebook/renameNotebook",
            data=body.get("data"),
            summary=f"已重命名笔记本为 {name}",
        )

    def remove(self, notebook_id: str) -> OperationResult:
        body = self.client.call("/api/notebook/removeNotebook", {"notebook": notebook_id})
        return OperationResult(
            endpoint="/api/notebook/removeNotebook",
            data=body.get("data"),
            summary=f"已删除笔记本 {notebook_id}",
        )

    def get_conf(self, notebook_id: str) -> OperationResult:
        body = self.client.call("/api/notebook/getNotebookConf", {"notebook": notebook_id})
        return OperationResult(
            endpoint="/api/notebook/getNotebookConf",
            data=body.get("data"),
            summary="已获取笔记本配置",
        )

    def find(self, keyword: str) -> OperationResult:
        notebooks = self.list().data
        matched = [item for item in notebooks if keyword.lower() in str(item.get("name", "")).lower()]
        return OperationResult(
            endpoint="/api/notebook/lsNotebooks",
            data=matched,
            tabular=True,
            columns=NOTEBOOK_COLUMNS,
            summary=f"匹配到 {len(matched)} 个笔记本",
        )

    def ensure_agent_workspace(self) -> OperationResult:
        notebooks = self.list().data
        for notebook in notebooks:
            if notebook.get("name") == "AgentWorkspace":
                return OperationResult(
                    endpoint="/api/notebook/lsNotebooks",
                    data=notebook,
                    summary="AgentWorkspace 已存在",
                )
        created = self.create("AgentWorkspace")
        return OperationResult(
            endpoint=created.endpoint,
            data=created.data,
            summary="已创建 AgentWorkspace",
        )
