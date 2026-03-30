import json
from pathlib import Path

EXPECTED_TOOLS = {
    "search_kb",
    "lookup_customer",
    "lookup_order",
    "propose_action",
    "create_or_escalate_ticket",
}

REQUIRED_TOP_LEVEL_KEYS = {
    "name",
    "version",
    "description",
    "input_schema",
    "output_schema",
    "error_schema",
}


def _load_contract(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_frozen_tool_contracts_exist() -> None:
    contract_dir = Path(__file__).resolve().parents[1] / "specs" / "05_tool_contracts"
    names = {p.stem for p in contract_dir.glob("*.json")}
    assert names == EXPECTED_TOOLS


def test_contract_shape_and_invariants() -> None:
    contract_dir = Path(__file__).resolve().parents[1] / "specs" / "05_tool_contracts"

    for path in sorted(contract_dir.glob("*.json")):
        contract = _load_contract(path)
        assert REQUIRED_TOP_LEVEL_KEYS.issubset(contract), f"Missing required keys in {path.name}"

        assert contract["name"] == path.stem
        assert contract["version"] == "1.0.0-day1-freeze"

        input_schema = contract["input_schema"]
        output_schema = contract["output_schema"]

        assert input_schema["type"] == "object"
        assert output_schema["type"] == "object"
        assert input_schema.get("additionalProperties") is False
        assert output_schema.get("additionalProperties") is False

        error_schema = contract["error_schema"]
        assert error_schema.get("$ref") == "shared_error_envelope_v1"


def test_propose_action_contract_enforces_approval_output() -> None:
    contract_path = (
        Path(__file__).resolve().parents[1] / "specs" / "05_tool_contracts" / "propose_action.json"
    )
    contract = _load_contract(contract_path)

    output_schema = contract["output_schema"]
    status_schema = output_schema["properties"]["status"]
    assert status_schema["const"] == "needs_human_approval"

    action_type_schema = contract["input_schema"]["properties"]["action_type"]
    assert set(action_type_schema["enum"]) == {"refund_request", "address_change", "cancel_order"}
