from __future__ import annotations

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult


class NotificationOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def push_msg(self, message: str, timeout: int = 7000) -> OperationResult:
        body = self.client.call("/api/notification/pushMsg", {"msg": message, "timeout": timeout})
        return OperationResult(
            endpoint="/api/notification/pushMsg",
            data=body.get("data"),
            summary="已推送通知消息",
        )

    def push_err_msg(self, message: str, timeout: int = 7000) -> OperationResult:
        body = self.client.call("/api/notification/pushErrMsg", {"msg": message, "timeout": timeout})
        return OperationResult(
            endpoint="/api/notification/pushErrMsg",
            data=body.get("data"),
            summary="已推送错误通知",
        )
