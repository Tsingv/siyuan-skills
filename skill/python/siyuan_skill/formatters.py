from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Sequence

from siyuan_skill.conversions import is_record_list, records_to_dataframe


@dataclass(slots=True)
class OperationResult:
    endpoint: str
    data: Any
    tabular: bool = False
    columns: Sequence[str] | None = None
    summary: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


def build_envelope(result: OperationResult, output_format: str) -> dict[str, Any]:
    meta = dict(result.meta)
    meta.setdefault("format", output_format)
    meta.setdefault("tabular", result.tabular)
    if result.tabular and is_record_list(result.data):
        meta.setdefault("row_count", len(result.data))
    if result.columns:
        meta.setdefault("columns", list(result.columns))
    if result.summary:
        meta.setdefault("summary", result.summary)
    return {
        "ok": True,
        "endpoint": result.endpoint,
        "data": result.data,
        "meta": meta,
    }


def render_result(result: OperationResult, output_format: str) -> str:
    normalized_format = output_format.lower()
    if normalized_format == "json":
        return json.dumps(build_envelope(result, normalized_format), ensure_ascii=False, indent=2, default=str)
    if normalized_format == "text":
        return _render_text(result)
    if normalized_format == "markdown":
        return _render_markdown(result)
    if normalized_format == "csv":
        return _render_csv(result)
    raise ValueError(f"不支持的输出格式: {output_format}")


def _render_text(result: OperationResult) -> str:
    if isinstance(result.data, str):
        return result.data
    if result.summary:
        return result.summary
    if result.tabular and is_record_list(result.data):
        return f"{result.endpoint}: {len(result.data)} rows"
    return json.dumps(result.data, ensure_ascii=False, indent=2, default=str)


def _render_markdown(result: OperationResult) -> str:
    if result.tabular and is_record_list(result.data):
        frame = records_to_dataframe(result.data, result.columns)
        total_rows = len(frame.index)
        display_frame = frame.head(50)
        header_lines = [f"- endpoint: `{result.endpoint}`", f"- rows: {total_rows}"]
        if total_rows > 50:
            header_lines.append("- showing: first 50 rows")
        table = display_frame.to_markdown(index=False)
        return "\n".join(header_lines) + "\n\n" + table
    if isinstance(result.data, str):
        return result.data
    code_block = json.dumps(result.data, ensure_ascii=False, indent=2, default=str)
    if result.summary:
        return f"{result.summary}\n\n```json\n{code_block}\n```"
    return f"```json\n{code_block}\n```"


def _render_csv(result: OperationResult) -> str:
    if not (result.tabular and is_record_list(result.data)):
        raise ValueError("csv 仅支持表格型结果")
    frame = records_to_dataframe(result.data, result.columns)
    return frame.to_csv(index=False)
