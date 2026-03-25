from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult
from siyuan_skill.operations.docs import DocOperations
from siyuan_skill.operations.notebooks import NotebookOperations

WORKSPACE_NAME = "AgentWorkspace"
WORKSPACE_PATTERN = r"^[0-9]{14}-[a-z0-9]{7}$"


class WorkspaceOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client
        self.notebooks = NotebookOperations(client)
        self.docs = DocOperations(client)

    @staticmethod
    def _resolve_notebook_id(payload: dict) -> str:
        if not isinstance(payload, dict):
            return ""
        if payload.get("id"):
            return payload["id"]
        notebook = payload.get("notebook")
        if isinstance(notebook, dict) and notebook.get("id"):
            return notebook["id"]
        return ""

    def ensure_workspace(self) -> OperationResult:
        return self.notebooks.ensure_agent_workspace()

    def write_to_workspace(self, category: str, title: str, markdown: str) -> OperationResult:
        notebook_id = self._resolve_notebook_id(self.ensure_workspace().data)
        path = f"/{category}/{title}"
        created = self.docs.create_markdown(notebook_id, path, markdown)
        created.meta["notebook_id"] = notebook_id
        created.meta["path"] = path
        return created

    def smart_write(
        self,
        markdown: str,
        title: str,
        notebook_hint: str | None = None,
        category: str | None = None,
    ) -> OperationResult:
        notebook_id = ""
        if notebook_hint:
            matched = self.notebooks.find(notebook_hint).data
            if matched:
                notebook_id = matched[0].get("id", "")
            elif _looks_like_notebook_id(notebook_hint):
                notebook_id = notebook_hint

        if not notebook_id:
            notebook_id = self._resolve_notebook_id(self.ensure_workspace().data)

        path = f"/{title}" if not category else f"/{category}/{title}"
        result = self.docs.create_markdown(notebook_id, path, markdown)
        result.meta["notebook_id"] = notebook_id
        result.meta["path"] = path
        return result


def _looks_like_notebook_id(value: str) -> bool:
    import re

    return bool(re.match(WORKSPACE_PATTERN, value))
