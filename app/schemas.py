from typing import Any, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str
    user_message: str = Field(min_length=1)


class ToolTrace(BaseModel):
    tool_name: str
    tool_args: dict[str, Any]
    result_summary: str


class ChatResponse(BaseModel):
    route: Literal["faq", "order_lookup", "action_request", "handoff"]
    answer: str
    citations: list[str] = []
    tool_traces: list[ToolTrace] = []
    state: dict[str, Any] = {}


class ApprovalDecision(BaseModel):
    approval_id: str
    decision: Literal["approved", "rejected"]
    reviewer: str
    reason: str | None = None
