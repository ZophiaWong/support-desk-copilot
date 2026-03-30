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
    citations: list[str] = Field(default_factory=list)
    tool_traces: list[ToolTrace] = Field(default_factory=list)
    state: dict[str, Any] = Field(default_factory=dict)


class ApprovalDecision(BaseModel):
    approval_id: str
    decision: Literal["approved", "rejected"]
    reviewer: str
    reason: str | None = None


class ToolErrorEnvelope(BaseModel):
    tool: str
    error_code: str
    message: str
    retryable: bool


class SearchKbInput(BaseModel):
    query: str = Field(min_length=1)


class SearchKbHit(BaseModel):
    article_id: str
    title: str
    snippet: str


class SearchKbOutput(BaseModel):
    tool: Literal["search_kb"]
    hits: list[SearchKbHit]


class LookupCustomerInput(BaseModel):
    identifier: str = Field(min_length=1)


class LookupCustomerRecord(BaseModel):
    customer_id: str
    email: str
    tags: list[str]


class LookupCustomerOutput(BaseModel):
    tool: Literal["lookup_customer"]
    customer: LookupCustomerRecord


class LookupOrderInput(BaseModel):
    identifier: str = Field(min_length=1)


class LookupOrderRecord(BaseModel):
    order_id: str
    status: str
    shipping_status: str
    total_amount: float


class LookupOrderOutput(BaseModel):
    tool: Literal["lookup_order"]
    order: LookupOrderRecord


class ProposeActionInput(BaseModel):
    action_type: Literal["refund_request", "address_change", "cancel_order"]
    payload: dict[str, Any] = Field(default_factory=dict)


class ProposeActionOutput(BaseModel):
    tool: Literal["propose_action"]
    approval_id: str
    action_type: str
    status: Literal["needs_human_approval"]
    payload: dict[str, Any] = Field(default_factory=dict)


class CreateOrEscalateTicketInput(BaseModel):
    reason: str = Field(min_length=1)
    priority: Literal["low", "medium", "high"]
    summary: str = Field(min_length=1)


class CreateOrEscalateTicketOutput(BaseModel):
    tool: Literal["create_or_escalate_ticket"]
    ticket_id: str
    status: str
    priority: str
    summary: str
    reason: str
