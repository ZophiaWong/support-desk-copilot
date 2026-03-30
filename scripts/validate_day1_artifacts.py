import json
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    specs = root / "specs"

    demo_text = (specs / "07_demo_script.md").read_text(encoding="utf-8")
    flow_count = demo_text.count("## Flow")
    require(flow_count == 3, f"Expected exactly 3 golden flows, found {flow_count}")
    require("needs_human_approval" in demo_text, "Demo flows must include approval-gate state")

    risky_text = (specs / "11_risky_actions.md").read_text(encoding="utf-8")
    for keyword in ("refund", "address", "cancel"):
        require(keyword in risky_text.lower(), f"Risk inventory missing keyword: {keyword}")

    eval_path = specs / "06_eval_cases.jsonl"
    eval_rows = [line for line in eval_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    require(len(eval_rows) >= 20, f"Expected at least 20 eval cases, found {len(eval_rows)}")

    categories = set()
    for row in eval_rows:
        categories.add(json.loads(row)["category"])
    for required in ("tool_selection", "retrieval_quality", "approval_gating", "risky_action_handling"):
        require(required in categories, f"Missing eval category: {required}")

    contract_names = {p.stem for p in (specs / "05_tool_contracts").glob("*.json")}
    expected_contracts = {
        "search_kb",
        "lookup_customer",
        "lookup_order",
        "propose_action",
        "create_or_escalate_ticket",
    }
    require(contract_names == expected_contracts, f"Contract set mismatch: {sorted(contract_names)}")

    print("Day 1 artifact validation passed.")


if __name__ == "__main__":
    main()
