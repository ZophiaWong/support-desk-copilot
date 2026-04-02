from app.llm import OllamaAdapter, OpenAIAdapter, RuleBasedLLMAdapter, get_llm_adapter
from app.schemas import ComposedResponse, ExtractionResult, JudgeCheckStatus, JudgeResult, OrchestrationState, ToolTrace


def test_provider_factory_supports_openai_and_ollama() -> None:
    assert isinstance(get_llm_adapter("openai"), OpenAIAdapter)
    assert isinstance(get_llm_adapter("ollama"), OllamaAdapter)


def test_rule_based_judge_reports_failed_checks_explicitly() -> None:
    adapter = RuleBasedLLMAdapter()
    extraction = ExtractionResult(route="action_request", order_id="ord_5102", action_type="refund_request")
    response = ComposedResponse(answer="Refund completed.")
    state = OrchestrationState(requires_human_approval=False, approval_status=None)

    result = adapter.judge(
        user_message="Refund order ord_5102",
        extraction=extraction,
        response=response,
        tool_traces=[ToolTrace(tool_name="lookup_order", tool_args={"identifier": "ord_5102"}, result_summary="...")],
        state=state,
    )

    assert isinstance(get_llm_adapter("anthropic"), RuleBasedLLMAdapter)
    assert result.passed is False
    assert result.policy_compliance == JudgeCheckStatus(
        status="fail", details="Sensitive actions remain approval-gated and evidence-backed."
    )
    assert result.tool_use_correctness.status == "fail"
    assert "policy_compliance" in result.failed_checks
    assert "tool_use_correctness" in result.failed_checks
