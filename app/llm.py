from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any

from app.schemas import (
    ComposedResponse,
    ExtractionResult,
    JudgeCheckStatus,
    JudgeResult,
    OrchestrationState,
    PlannerAction,
    ToolTrace,
)

ORDER_ID_RE = re.compile(r"\bord_\d+\b", re.IGNORECASE)
CUSTOMER_ID_RE = re.compile(r"\bcust_\d+\b", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)


def _normalize_text(value: str) -> str:
    return value.lower().strip()


class BaseLLMAdapter(ABC):
    provider_name: str = "stub"

    @abstractmethod
    def extract(self, session_messages: list[dict[str, Any]], user_message: str) -> ExtractionResult:
        raise NotImplementedError

    @abstractmethod
    def plan_next_action(
        self,
        user_message: str,
        extraction: ExtractionResult,
        tool_traces: list[ToolTrace],
        state: OrchestrationState,
        remaining_turns: int,
        remaining_tool_calls: int,
    ) -> PlannerAction:
        raise NotImplementedError

    @abstractmethod
    def compose_response(
        self,
        user_message: str,
        extraction: ExtractionResult,
        tool_results: dict[str, dict[str, Any]],
        state: OrchestrationState,
    ) -> ComposedResponse:
        raise NotImplementedError

    @abstractmethod
    def judge(
        self,
        user_message: str,
        extraction: ExtractionResult,
        response: ComposedResponse,
        tool_traces: list[ToolTrace],
        state: OrchestrationState,
    ) -> JudgeResult:
        raise NotImplementedError


class RuleBasedLLMAdapter(BaseLLMAdapter):
    provider_name = "rule-based"

    def extract(self, session_messages: list[dict[str, Any]], user_message: str) -> ExtractionResult:
        text = _normalize_text(user_message)
        order_match = ORDER_ID_RE.search(user_message)
        customer_match = CUSTOMER_ID_RE.search(user_message)
        email_match = EMAIL_RE.search(user_message)

        route = "handoff"
        action_type = None
        ambiguity_reason = None

        faq_markers = (
            "policy",
            "refund window",
            "return policy",
            "what is",
            "how do",
            "can opened items",
            "can unopened items",
        )
        action_markers = ("refund", "cancel", "address change", "change address")

        if any(token in text for token in faq_markers):
            route = "faq"
        elif any(token in text for token in action_markers):
            route = "action_request"
            if "refund" in text:
                action_type = "refund_request"
            elif "cancel" in text:
                action_type = "cancel_order"
            else:
                action_type = "address_change"
        elif any(
            token in text
            for token in ("where is", "track", "tracking", "status of", "shipping update", "order status")
        ):
            route = "order_lookup"
        elif any(token in text for token in ("escalate", "human", "manual review", "cannot verify")):
            route = "handoff"

        if route in {"action_request", "order_lookup"} and not order_match:
            ambiguity_reason = "missing_order_id"
        if route == "action_request" and action_type is None:
            ambiguity_reason = "missing_action_type"

        confidence = 0.95 if ambiguity_reason is None else 0.35
        return ExtractionResult(
            route=route,
            order_id=order_match.group(0).lower() if order_match else None,
            customer_id=customer_match.group(0).lower() if customer_match else None,
            customer_email=email_match.group(0).lower() if email_match else None,
            action_type=action_type,
            confidence=confidence,
            ambiguity_reason=ambiguity_reason,
        )

    def plan_next_action(
        self,
        user_message: str,
        extraction: ExtractionResult,
        tool_traces: list[ToolTrace],
        state: OrchestrationState,
        remaining_turns: int,
        remaining_tool_calls: int,
    ) -> PlannerAction:
        tool_names = [trace.tool_name for trace in tool_traces]

        if extraction.route == "faq":
            if "search_kb" not in tool_names:
                return PlannerAction(action_type="tool", tool_name="search_kb", tool_args={"query": user_message})
            return PlannerAction(action_type="respond")

        if extraction.route == "order_lookup":
            if "lookup_order" not in tool_names:
                return PlannerAction(
                    action_type="tool",
                    tool_name="lookup_order",
                    tool_args={"identifier": extraction.order_id},
                )
            return PlannerAction(action_type="respond")

        if extraction.route == "action_request":
            if "lookup_order" not in tool_names:
                return PlannerAction(
                    action_type="tool",
                    tool_name="lookup_order",
                    tool_args={"identifier": extraction.order_id},
                )
            if "propose_action" not in tool_names:
                return PlannerAction(
                    action_type="tool",
                    tool_name="propose_action",
                    tool_args={
                        "action_type": extraction.action_type,
                        "payload": {"order_id": extraction.order_id, "reason": user_message},
                    },
                )
            return PlannerAction(action_type="respond")

        if "create_or_escalate_ticket" not in tool_names and remaining_tool_calls > 0:
            return PlannerAction(
                action_type="tool",
                tool_name="create_or_escalate_ticket",
                tool_args={
                    "reason": state.handoff_reason or extraction.ambiguity_reason or "insufficient_information",
                    "priority": "medium",
                    "summary": user_message,
                },
            )
        return PlannerAction(action_type="respond")

    def compose_response(
        self,
        user_message: str,
        extraction: ExtractionResult,
        tool_results: dict[str, dict[str, Any]],
        state: OrchestrationState,
    ) -> ComposedResponse:
        if extraction.route == "faq":
            hits = tool_results.get("search_kb", {}).get("hits", [])
            if hits:
                top_hit = hits[0]
                return ComposedResponse(
                    answer=f"According to {top_hit['title']}, {top_hit['snippet']}",
                    citations=[hit["article_id"] for hit in hits],
                )
            return ComposedResponse(answer="I could not find policy evidence, so I handed this off.")

        if extraction.route == "order_lookup":
            order = tool_results.get("lookup_order", {}).get("order", {})
            return ComposedResponse(
                answer=(
                    f"Order {order.get('order_id')} is currently {order.get('shipping_status')} "
                    f"with overall status {order.get('status')}."
                ),
            )

        if extraction.route == "action_request":
            proposal = tool_results.get("propose_action", {})
            order = tool_results.get("lookup_order", {}).get("order", {})
            return ComposedResponse(
                answer=(
                    f"I reviewed order {order.get('order_id')} and created approval request "
                    f"{proposal.get('approval_id')} for {proposal.get('action_type')}."
                ),
            )

        ticket_id = state.ticket_id or tool_results.get("create_or_escalate_ticket", {}).get("ticket_id")
        ticket_phrase = f"escalation ticket {ticket_id}" if ticket_id else "an escalation request"
        return ComposedResponse(
            answer=(
                "I could not verify enough information to proceed safely, "
                f"so I created {ticket_phrase}."
            ),
        )

    def judge(
        self,
        user_message: str,
        extraction: ExtractionResult,
        response: ComposedResponse,
        tool_traces: list[ToolTrace],
        state: OrchestrationState,
    ) -> JudgeResult:
        tool_names = [trace.tool_name for trace in tool_traces]

        def _check(status: bool, details: str) -> JudgeCheckStatus:
            return JudgeCheckStatus(status="pass" if status else "fail", details=details)

        route_ok = extraction.route != "handoff" or state.ticket_id is not None or state.handoff_reason is not None
        if extraction.route == "faq":
            tool_ok = tool_names == ["search_kb"]
            policy_ok = len(response.citations) > 0
        elif extraction.route == "order_lookup":
            tool_ok = tool_names == ["lookup_order"]
            policy_ok = "lookup_order" in tool_names
        elif extraction.route == "action_request":
            tool_ok = tool_names == ["lookup_order", "propose_action"]
            policy_ok = state.requires_human_approval and state.approval_status == "needs_human_approval"
        else:
            tool_ok = "create_or_escalate_ticket" in tool_names or state.ticket_id is not None
            policy_ok = True

        intent_ok = bool(response.answer.strip())

        result = JudgeResult(
            passed=route_ok and tool_ok and policy_ok and intent_ok,
            route_correctness=_check(route_ok, "Route matches the extracted intent or safe handoff fallback."),
            tool_use_correctness=_check(tool_ok, "Tool usage matches the expected path for the selected route."),
            policy_compliance=_check(policy_ok, "Sensitive actions remain approval-gated and evidence-backed."),
            intent_satisfaction=_check(intent_ok, "The response contains a user-facing answer."),
            failed_checks=[],
            notes=f"Judged response for provider stub {self.provider_name}.",
        )
        if result.route_correctness.status == "fail":
            result.failed_checks.append("route_correctness")
        if result.tool_use_correctness.status == "fail":
            result.failed_checks.append("tool_use_correctness")
        if result.policy_compliance.status == "fail":
            result.failed_checks.append("policy_compliance")
        if result.intent_satisfaction.status == "fail":
            result.failed_checks.append("intent_satisfaction")
        return result


class AnthropicAdapter(RuleBasedLLMAdapter):
    provider_name = "anthropic"


class OpenAIAdapter(RuleBasedLLMAdapter):
    provider_name = "openai"


class OllamaAdapter(RuleBasedLLMAdapter):
    provider_name = "ollama"


def get_llm_adapter(provider: str) -> BaseLLMAdapter:
    normalized = provider.lower().strip()
    if normalized == "anthropic":
        return AnthropicAdapter()
    if normalized == "ollama":
        return OllamaAdapter()
    return OpenAIAdapter()
