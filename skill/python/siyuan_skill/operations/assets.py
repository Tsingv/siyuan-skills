from __future__ import annotations

from pathlib import Path

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult


class AssetOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def upload(self, file_path: str, assets_dir: str = "/assets/") -> OperationResult:
        local_path = Path(file_path)
        with local_path.open("rb") as file_obj:
            body = self.client.upload(
                "/api/asset/upload",
                data={"assetsDirPath": assets_dir},
                files={"file[]": (local_path.name, file_obj)},
            )
        return OperationResult(
            endpoint="/api/asset/upload",
            data=body.get("data"),
            summary=f"已上传资源 {local_path.name}",
        )
