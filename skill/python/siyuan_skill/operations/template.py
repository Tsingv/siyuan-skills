from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult


class TemplateOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def render(self, doc_id: str, path: str) -> OperationResult:
        body = self.client.call("/api/template/render", {"id": doc_id, "path": path})
        return OperationResult(
            endpoint="/api/template/render",
            data=body.get("data"),
            summary="已渲染模板",
        )

    def render_sprig(self, template: str) -> OperationResult:
        body = self.client.call("/api/template/renderSprig", {"template": template})
        return OperationResult(
            endpoint="/api/template/renderSprig",
            data=body.get("data"),
            summary="已渲染 Sprig 模板",
        )
