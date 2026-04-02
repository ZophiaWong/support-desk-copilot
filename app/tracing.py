from dataclasses import dataclass, asdict
from typing import Any

from app.schemas import ToolTrace


@dataclass
class TraceEvent:
    tool_name: str
    tool_args: dict[str, Any]
    result_summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_tool_trace(self) -> ToolTrace:
        return ToolTrace(
            tool_name=self.tool_name,
            tool_args=self.tool_args,
            result_summary=self.result_summary,
        )
