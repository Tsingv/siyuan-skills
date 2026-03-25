from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult


class SystemOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def version(self) -> OperationResult:
        body = self.client.call("/api/system/version", {})
        return OperationResult(
            endpoint="/api/system/version",
            data=body.get("data"),
            summary="已获取思源版本",
        )

    def get_conf(self) -> OperationResult:
        body = self.client.call("/api/system/getConf", {})
        return OperationResult(
            endpoint="/api/system/getConf",
            data=body.get("data"),
            summary="已获取系统配置",
        )

    def boot_progress(self) -> OperationResult:
        body = self.client.call("/api/system/bootProgress", {})
        return OperationResult(
            endpoint="/api/system/bootProgress",
            data=body.get("data"),
            summary="已获取启动进度",
        )
