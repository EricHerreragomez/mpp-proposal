"""Send each question in tests/test_cases.md to assistant.answer and print the result."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import assistant

_ROW = re.compile(r"^\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$")


def load_cases(path: Path) -> list[tuple[str, str]]:
    cases: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        if "Question" in line and "Expected" in line:
            continue
        if not line.replace("|", "").replace("-", "").replace(":", "").strip():
            continue
        match = _ROW.match(line)
        if not match:
            continue
        question, expected = match.group(1).strip(), match.group(2).strip()
        if len(question) >= 2 and question[0] == '"' and question[-1] == '"':
            question = question[1:-1]
        cases.append((question, expected))
    return cases


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add a key.")
    cases = load_cases(ROOT / "tests" / "test_cases.md")
    if not cases:
        sys.exit("No cases found in tests/test_cases.md")
    for question, expected in cases:
        print("=" * 60)
        print(f"Q: {question}")
        print(f"Expected: {expected}")
        print("Answer:")
        print(assistant.answer(question))
        print()


if __name__ == "__main__":
    main()
