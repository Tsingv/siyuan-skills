from __future__ import annotations

from typing import Any

import requests

from siyuan_skill.auth import SiYuanAuthManager
from siyuan_skill.config import SiYuanConfig
from siyuan_skill.errors import SiYuanApiError, SiYuanConnectionError


class SiYuanClient:
    def __init__(self, config: SiYuanConfig | None = None):
        self.config = config or SiYuanConfig.load()
        self.session = requests.Session()
        self.auth = SiYuanAuthManager(self.config, self.session)

    def call(self, endpoint: str, payload: dict[str, Any] | None = None, *, retry_auth: bool = True) -> dict[str, Any]:
        self.auth.ensure_authenticated()
        body = self._post(endpoint, payload or {})
        if body.get("code") == 1 and retry_auth:
            self.auth.reauthenticate()
            body = self._post(endpoint, payload or {})
        code = body.get("code", -1)
        if code != 0:
            raise SiYuanApiError(endpoint, code, body.get("msg") or "Unknown error", body)
        return body

    def upload(self, endpoint: str, *, data: dict[str, Any], files: dict[str, Any]) -> dict[str, Any]:
        self.auth.ensure_authenticated()
        url = self.url(endpoint)
        headers = self.auth.get_headers()
        try:
            response = self.session.post(
                url,
                data=data,
                files=files,
                headers=headers,
                timeout=self.config.timeout,
            )
        except requests.RequestException as exc:
            raise SiYuanConnectionError(f"无法连接到思源接口 {url}") from exc
        try:
            body = response.json()
        except ValueError as exc:
            raise SiYuanApiError(endpoint, response.status_code, "响应不是有效 JSON", {"text": response.text[:500]}) from exc
        code = body.get("code", -1)
        if code != 0:
            raise SiYuanApiError(endpoint, code, body.get("msg") or "Unknown error", body)
        return body

    def url(self, endpoint: str) -> str:
        return f"{self.config.host}{endpoint}"

    def health_status(self) -> dict[str, Any]:
        version = self.call("/api/system/version", {}).get("data")
        notebooks = self.call("/api/notebook/lsNotebooks", {}).get("data", {}).get("notebooks", [])
        return {
            "version": version,
            "notebook_count": len(notebooks),
        }

    def _post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = self.url(endpoint)
        headers = {
            "Content-Type": "application/json",
            **self.auth.get_headers(),
        }
        try:
            response = self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.config.timeout,
            )
        except requests.RequestException as exc:
            raise SiYuanConnectionError(f"无法连接到思源接口 {url}") from exc
        try:
            return response.json()
        except ValueError as exc:
            raise SiYuanApiError(endpoint, response.status_code, "响应不是有效 JSON", {"text": response.text[:500]}) from exc
