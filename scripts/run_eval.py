import argparse
import json
from pathlib import Path

REQUIRED_KEYS = {
    "id",
    "category",
    "input",
    "expected_route",
    "expected_tools",
    "requires_citation",
    "requires_human_approval",
    "pass_criteria",
    "deterministic_seed",
}

ALLOWED_CATEGORIES = {
    "tool_selection",
    "retrieval_quality",
    "approval_gating",
    "risky_action_handling",
}


def load_cases(eval_path: Path) -> list[dict]:
    cases: list[dict] = []
    for lineno, raw in enumerate(eval_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            case = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON at line {lineno}: {exc}") from exc
        missing = REQUIRED_KEYS - set(case)
        if missing:
            raise ValueError(f"Case {case.get('id', f'line-{lineno}')} missing keys: {sorted(missing)}")
        if case["category"] not in ALLOWED_CATEGORIES:
            raise ValueError(f"Case {case['id']} has unsupported category '{case['category']}'")
        if not isinstance(case["expected_tools"], list) or not case["expected_tools"]:
            raise ValueError(f"Case {case['id']} must define at least one expected tool")
        if not isinstance(case["pass_criteria"], list) or not case["pass_criteria"]:
            raise ValueError(f"Case {case['id']} must define at least one pass criterion")
        cases.append(case)
    return cases


def summarize(cases: list[dict]) -> dict[str, int]:
    counts = {category: 0 for category in sorted(ALLOWED_CATEGORIES)}
    for case in cases:
        counts[case["category"]] += 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and summarize offline eval cases.")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate structure only and print summary without endpoint execution.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    eval_path = root / "specs" / "06_eval_cases.jsonl"

    cases = load_cases(eval_path)
    counts = summarize(cases)

    print(f"Loaded {len(cases)} eval cases from {eval_path}.")
    print("Category distribution:")
    for category, count in counts.items():
        print(f"- {category}: {count}")

    if len(cases) < 20:
        raise SystemExit("Expected at least 20 eval cases for Day 1 baseline.")

    missing_categories = [name for name, count in counts.items() if count == 0]
    if missing_categories:
        raise SystemExit(f"Missing required categories: {', '.join(missing_categories)}")

    if args.validate_only:
        print("Validation-only mode complete: eval seed set is structurally valid.")
        return

    print("No endpoint execution configured in this MVP runner yet.")
    print("Use --validate-only for Day 1 reproducibility checks.")


if __name__ == "__main__":
    main()
