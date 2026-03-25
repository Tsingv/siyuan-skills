from __future__ import annotations

from typing import Any

from siyuan_skill.client import SiYuanClient
from siyuan_skill.formatters import OperationResult


class RiffOperations:
    def __init__(self, client: SiYuanClient):
        self.client = client

    def create_deck(self, name: str) -> OperationResult:
        body = self.client.call("/api/riff/createRiffDeck", {"name": name})
        return OperationResult(
            endpoint="/api/riff/createRiffDeck",
            data=body.get("data"),
            summary=f"已创建牌组 {name}",
        )

    def get_decks(self) -> OperationResult:
        body = self.client.call("/api/riff/getRiffDecks", {})
        data = body.get("data") or []
        return OperationResult(
            endpoint="/api/riff/getRiffDecks",
            data=data,
            tabular=isinstance(data, list),
            summary=f"共 {len(data) if isinstance(data, list) else 0} 个牌组",
        )

    def add_cards(self, deck_id: str, block_ids: list[str]) -> OperationResult:
        body = self.client.call("/api/riff/addRiffCards", {"deckID": deck_id, "blockIDs": block_ids})
        return OperationResult(
            endpoint="/api/riff/addRiffCards",
            data=body.get("data"),
            summary=f"已向牌组 {deck_id} 添加 {len(block_ids)} 张卡片",
        )

    def get_due_cards(self, deck_id: str | None = None) -> OperationResult:
        body = self.client.call("/api/riff/getRiffDueCards", {"deckID": deck_id or ""})
        data = body.get("data", {})
        return OperationResult(
            endpoint="/api/riff/getRiffDueCards",
            data=data,
            summary="已获取待复习卡片",
        )

    def review_card(self, deck_id: str, card_id: str, rating: int) -> OperationResult:
        body = self.client.call(
            "/api/riff/reviewRiffCard",
            {"deckID": deck_id, "cardID": card_id, "rating": rating},
        )
        return OperationResult(
            endpoint="/api/riff/reviewRiffCard",
            data=body.get("data"),
            summary="已提交复习结果",
        )
