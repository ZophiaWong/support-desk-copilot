from __future__ import annotations

from app.config import settings
from app.llm import BaseLLMAdapter, RuleBasedLLMAdapter
from app.orchestrator import handle_message
from app.persistence import SQLiteStore
from app.schemas import ComposedResponse, ExtractionResult, JudgeCheckStatus, JudgeResult, OrchestrationState, PlannerAction


class ScriptedAdapter(BaseLLMAdapter):
    provider_name = "scripted"

    def __init__(self, extraction: ExtractionResult, actions: list[PlannerAction]):
        self.extraction = extraction
        self.actions = list(actions)

    def extract(self, session_messages, user_message):
        return self.extraction

    def plan_next_action(self, user_message, extraction, tool_traces, state, remaining_turns, remaining_tool_calls):
        if self.actions:
            return self.actions.pop(0)
        return PlannerAction(action_type="respond")

    def compose_response(self, user_message, extraction, tool_results, state):
        if extraction.route == "handoff":
            return ComposedResponse(answer="Fallback handoff response.")
        return ComposedResponse(answer="Scripted response.")

    def judge(self, user_message, extraction, response, tool_traces, state):
        return JudgeResult(
            passed=True,
            route_correctness=JudgeCheckStatus(status="pass"),
            tool_use_correctness=JudgeCheckStatus(status="pass"),
            policy_compliance=JudgeCheckStatus(status="pass"),
            intent_satisfaction=JudgeCheckStatus(status="pass"),
            failed_checks=[],
            notes="scripted",
        )


def test_faq_flow_runs_end_to_end_with_citation() -> None:
    store = SQLiteStore(settings.sqlite_db_path)
    response = handle_message(
        "sess-faq",
        "What is the refund window for unopened items?",
        adapter=RuleBasedLLMAdapter(),
        store=store,
    )

    assert response.route == "faq"
    assert [trace.tool_name for trace in response.tool_traces] == ["search_kb"]
    assert response.citations
    assert response.state["judge_result"]["passed"] is True


def test_order_lookup_flow_uses_verified_order_data() -> None:
    store = SQLiteStore(settings.sqlite_db_path)
    response = handle_message(
        "sess-order",
        "Where is order ord_5102 right now?",
        adapter=RuleBasedLLMAdapter(),
        store=store,
    )

    assert response.route == "order_lookup"
    assert [trace.tool_name for trace in response.tool_traces] == ["lookup_order"]
    assert response.state["order_status"] == "in_transit"
    assert "ord_5102" in response.answer


def test_action_request_flow_persists_approval_request() -> None:
    store = SQLiteStore(settings.sqlite_db_path)
    response = handle_message(
        "sess-action",
        "Please refund my shipped order ord_5102.",
        adapter=RuleBasedLLMAdapter(),
        store=store,
    )

    assert response.route == "action_request"
    assert [trace.tool_name for trace in response.tool_traces] == ["lookup_order", "propose_action"]
    assert response.state["approval_status"] == "needs_human_approval"
    approval = store.get_approval_request(response.state["approval_id"])
    assert approval is not None
    assert approval["session_id"] == "sess-action"


def test_ambiguous_extraction_fails_closed_to_handoff() -> None:
    store = SQLiteStore(settings.sqlite_db_path)
    response = handle_message(
        "sess-ambiguous",
        "Please refund my shipped order.",
        adapter=RuleBasedLLMAdapter(),
        store=store,
    )

    assert response.route == "handoff"
    assert response.state["handoff_reason"] == "missing_order_id"
    assert response.state["ticket_id"].startswith("tkt_")


def test_loop_limit_falls_back_to_safe_handoff() -> None:
    settings.max_llm_turns = 0
    settings.max_tool_calls = 1
    store = SQLiteStore(settings.sqlite_db_path)

    response = handle_message(
        "sess-limit",
        "What is the refund window for unopened items?",
        adapter=RuleBasedLLMAdapter(),
        store=store,
    )

    assert response.route == "handoff"
    assert response.state["handoff_reason"] == "loop_limit_exceeded"
    assert response.state["ticket_id"].startswith("tkt_")


def test_approval_review_events_are_persisted_separately() -> None:
    from app.schemas import ApprovalDecision

    store = SQLiteStore(settings.sqlite_db_path)
    response = handle_message(
        "sess-review",
        "Please refund my shipped order ord_5102.",
        adapter=RuleBasedLLMAdapter(),
        store=store,
    )
    review = store.record_approval_review(
        ApprovalDecision(
            approval_id=response.state["approval_id"],
            decision="approved",
            reviewer="agent@example.com",
            reason="Verified with policy.",
        ),
        session_id="sess-review",
    )
    reviews = store.get_approval_reviews(response.state["approval_id"])

    assert review.session_id == "sess-review"
    assert len(reviews) == 1
    assert reviews[0].decision == "approved"


def test_scripted_adapter_is_a_deterministic_test_double() -> None:
    settings.enable_judge = True
    store = SQLiteStore(settings.sqlite_db_path)
    adapter = ScriptedAdapter(
        extraction=ExtractionResult(route="handoff", ambiguity_reason="test_override"),
        actions=[PlannerAction(action_type="respond")],
    )

    response = handle_message("sess-scripted", "anything", adapter=adapter, store=store)

    assert response.route == "handoff"
    assert response.answer == "Fallback handoff response."
