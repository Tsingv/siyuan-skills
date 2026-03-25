from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

import pandas as pd


DEFAULT_MAX_CELL_LENGTH = 160


def is_record_list(data: Any) -> bool:
    return isinstance(data, list) and all(isinstance(item, dict) for item in data)


def truncate_text(value: str, max_length: int = DEFAULT_MAX_CELL_LENGTH) -> str:
    if len(value) <= max_length:
        return value
    return f"{value[: max_length - 1]}…"


def normalize_scalar(value: Any, max_cell_length: int = DEFAULT_MAX_CELL_LENGTH) -> Any:
    if value is None:
        return ""
    if isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, (dict, list, tuple, set)):
        return truncate_text(json.dumps(value, ensure_ascii=False), max_cell_length)
    return truncate_text(str(value), max_cell_length)


def records_to_dataframe(
    records: Sequence[dict[str, Any]],
    columns: Sequence[str] | None = None,
    *,
    max_cell_length: int = DEFAULT_MAX_CELL_LENGTH,
) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=list(columns or []))

    normalized = []
    for record in records:
        normalized.append({
            key: normalize_scalar(value, max_cell_length=max_cell_length)
            for key, value in record.items()
        })

    frame = pd.DataFrame(normalized)
    if columns:
        for column in columns:
            if column not in frame.columns:
                frame[column] = ""
        trailing_columns = [column for column in frame.columns if column not in columns]
        frame = frame[[*columns, *trailing_columns]]
    return frame.fillna("")
