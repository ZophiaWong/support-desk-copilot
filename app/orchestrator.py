from __future__ import annotations

from typing import Any

from app.config import settings
from app.exceptions import ToolError
from app.llm import BaseLLMAdapter, get_llm_adapter
from app.persistence import SQLiteStore
from app.schemas import (
    ChatResponse,
    ComposedResponse,
    ExtractionResult,
    OrchestrationState,
    PlannerAction,
    ToolTrace,
)
from app.tools import (
    create_or_escalate_ticket,
    lookup_customer,
    lookup_order,
    propose_action,
    search_kb,
)

TOOL_REGISTRY = {
    "search_kb": search_kb,
    "lookup_customer": lookup_customer,
    "lookup_order": lookup_order,
    "propose_action": propose_action,
    "create_or_escalate_ticket": create_or_escalate_ticket,
}


def _trace(tool_name: str, tool_args: dict[str, Any], result: dict[str, Any]) -> ToolTrace:
    return ToolTrace(
        tool_name=tool_name,
        tool_args=tool_args,
        result_summary=str(result)[:240],
    )


def _policy_gate(extraction: ExtractionResult) -> tuple[ExtractionResult, str | None]:
    if extraction.route in {"order_lookup", "action_request"} and not extraction.order_id:
        return extraction.model_copy(update={"route": "handoff"}), "missing_order_id"
    if extraction.route == "action_request" and not extraction.action_type:
        return extraction.model_copy(update={"route": "handoff"}), "missing_action_type"
    return extraction, None


def _execute_tool(
    session_id: str,
    route: str,
    state: OrchestrationState,
    store: SQLiteStore,
    tool_name: str,
    tool_args: dict[str, Any],
) -> tuple[ToolTrace, dict[str, Any]]:
    result = TOOL_REGISTRY[tool_name](**tool_args)
    trace = _trace(tool_name, tool_args, result)
    store.record_tool_trace(session_id, trace)

    if tool_name == "lookup_order":
        state.order_status = result["order"]["shipping_status"]
    elif tool_name == "propose_action":
        state.requires_human_approval = True
        state.approval_status = result["status"]
        state.approval_id = result["approval_id"]
        store.record_approval_request(
            session_id=session_id,
            route=route,
            approval_id=result["approval_id"],
            action_type=result["action_type"],
            status=result["status"],
            payload=result["payload"],
        )
    elif tool_name == "create_or_escalate_ticket":
        state.ticket_id = result["ticket_id"]
        store.record_ticket(session_id, result)

    return trace, result


def _safe_handoff(
    session_id: str,
    user_message: str,
    extraction: ExtractionResult,
    state: OrchestrationState,
    store: SQLiteStore,
    traces: list[ToolTrace],
    results: dict[str, dict[str, Any]],
) -> None:
    if state.ticket_id is not None:
        return
    if len(traces) >= settings.max_tool_calls:
        return
    trace, result = _execute_tool(
        session_id=session_id,
        route="handoff",
        state=state,
        store=store,
        tool_name="create_or_escalate_ticket",
        tool_args={
            "reason": state.handoff_reason or extraction.ambiguity_reason or "insufficient_information",
            "priority": "medium",
            "summary": user_message,
        },
    )
    traces.append(trace)
    results["create_or_escalate_ticket"] = result


def _dump_state(state: OrchestrationState) -> dict[str, Any]:
    payload = state.model_dump(exclude_none=True)
    judge = payload.get("judge_result")
    if judge is not None and hasattr(judge, "model_dump"):
        payload["judge_result"] = judge.model_dump(exclude_none=True)
    return payload


def handle_message(
    session_id: str,
    user_message: str,
    adapter: BaseLLMAdapter | None = None,
    store: SQLiteStore | None = None,
) -> ChatResponse:
    adapter = adapter or get_llm_adapter(settings.model_provider)
    store = store or SQLiteStore()
    store.ensure_session(session_id)
    store.record_message(session_id, "user", user_message)

    session_messages = store.get_messages(session_id)
    extraction = adapter.extract(session_messages, user_message)
    extraction = ExtractionResult.model_validate(extraction)
    extraction, handoff_reason = _policy_gate(extraction)

    state = OrchestrationState(handoff_reason=handoff_reason or extraction.ambiguity_reason)
    traces: list[ToolTrace] = []
    tool_results: dict[str, dict[str, Any]] = {}
    composed: ComposedResponse | None = None
    route = extraction.route
    turns = 0

    while turns < settings.max_llm_turns:
        remaining_turns = settings.max_llm_turns - turns
        remaining_tool_calls = settings.max_tool_calls - len(traces)
        action = PlannerAction.model_validate(
            adapter.plan_next_action(
                user_message=user_message,
                extraction=extraction,
                tool_traces=traces,
                state=state,
                remaining_turns=remaining_turns,
                remaining_tool_calls=remaining_tool_calls,
            )
        )
        turns += 1

        if action.action_type == "respond":
            composed = adapter.compose_response(user_message, extraction, tool_results, state)
            break

        if action.action_type == "handoff":
            route = "handoff"
            extraction = extraction.model_copy(update={"route": "handoff"})
            state.handoff_reason = action.handoff_reason or state.handoff_reason or "planner_handoff"
            continue

        if len(traces) >= settings.max_tool_calls:
            route = "handoff"
            extraction = extraction.model_copy(update={"route": "handoff"})
            state.handoff_reason = state.handoff_reason or "loop_limit_exceeded"
            break

        try:
            trace, result = _execute_tool(
                session_id=session_id,
                route=route,
                state=state,
                store=store,
                tool_name=action.tool_name,
                tool_args=action.tool_args,
            )
            traces.append(trace)
            tool_results[action.tool_name] = result
        except ToolError as exc:
            route = "handoff"
            extraction = extraction.model_copy(update={"route": "handoff"})
            state.handoff_reason = f"{exc.tool}:{exc.error_code}"
            break

    if composed is None:
        route = "handoff"
        extraction = extraction.model_copy(update={"route": "handoff"})
        state.handoff_reason = state.handoff_reason or "loop_limit_exceeded"
        _safe_handoff(session_id, user_message, extraction, state, store, traces, tool_results)
        composed = adapter.compose_response(user_message, extraction, tool_results, state)

    if settings.enable_judge:
        state.judge_result = adapter.judge(user_message, extraction, composed, traces, state)

    response = ChatResponse(
        route=route,
        answer=composed.answer,
        citations=composed.citations,
        tool_traces=traces,
        state=_dump_state(state),
    )
    store.record_message(
        session_id,
        "assistant",
        response.answer,
        metadata={"route": response.route, "state": response.state, "citations": response.citations},
    )
    return response
