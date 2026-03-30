from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class TraceEvent:
    tool_name: str
    tool_args: dict[str, Any]
    result_summary: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
