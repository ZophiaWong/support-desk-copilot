import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
eval_path = root / "specs" / "06_eval_cases.jsonl"

total = 0
for line in eval_path.read_text(encoding="utf-8").splitlines():
    if line.strip():
        total += 1

print(f"Loaded {total} eval cases.")
print("TODO: connect to /chat endpoint and compute route accuracy, citation coverage, and approval miss rate.")
