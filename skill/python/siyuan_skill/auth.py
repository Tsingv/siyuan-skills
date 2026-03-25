from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

from siyuan_skill.config import SiYuanConfig
from siyuan_skill.errors import SiYuanAuthError, SiYuanConnectionError


class SiYuanAuthManager:
    def __init__(self, config: SiYuanConfig, session: requests.Session):
        self.config = config
        self.session = session
        self.explicit_token = config.token.strip()
        self.token = self.explicit_token or self._load_cached_token()

    def get_headers(self) -> dict[str, str]:
        if self.token:
            return {"Authorization": f"Token {self.token}"}
        return {}

    def ensure_authenticated(self) -> None:
        if self.token or self.session.cookies or not self.config.password:
            return
        self.login()

    def reauthenticate(self) -> None:
        self.session.cookies.clear()
        self.invalidate_cache()
        self.token = ""
        if self.explicit_token:
            self.token = self.explicit_token
            return
        if self.config.password:
            self.login()

    def login(self) -> None:
        if not self.config.password:
            raise SiYuanAuthError("未设置 SIYUAN_TOKEN 或 PASSWORD。")

        login_payload = self._post_without_auth(
            "/api/system/loginAuth",
            {"authCode": self.config.password},
        )
        if login_payload.get("code") != 0:
            raise SiYuanAuthError(login_payload.get("msg") or "登录失败。")

        conf_payload = self._post_without_auth("/api/system/getConf", {})
        token = (
            conf_payload.get("data", {})
            .get("conf", {})
            .get("api", {})
            .get("token", "")
            .strip()
        )
        self.token = token
        if token:
            self._save_cached_token(token)

    def invalidate_cache(self) -> None:
        cache_file = self.config.cache_file
        if cache_file.exists():
            cache_file.unlink(missing_ok=True)

    def _load_cached_token(self) -> str:
        cache_file = self.config.cache_file
        if not cache_file.exists():
            return ""
        try:
            payload = json.loads(cache_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return ""
        return str(payload.get("token", "")).strip()

    def _save_cached_token(self, token: str) -> None:
        self.config.ensure_cache_parent()
        payload = {"token": token}
        self.config.cache_file.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _post_without_auth(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.config.host}{endpoint}"
        try:
            response = self.session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.config.timeout,
            )
        except requests.RequestException as exc:
            raise SiYuanConnectionError(f"无法连接到思源接口 {url}") from exc
        try:
            return response.json()
        except ValueError as exc:
            raise SiYuanAuthError(f"认证接口返回了非 JSON 响应: {url}") from exc
