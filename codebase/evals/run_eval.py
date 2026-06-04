from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from codebase.chatbot_parser.openai_parser import OpenAIParserError
from codebase.food_chatbot.answerer import FinalAnswerError
from codebase.food_chatbot.pipeline import run_food_chatbot


DEFAULT_CASES_PATH = Path(__file__).with_name("eval_cases.json")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Run prompt/AI flow eval cases.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES_PATH))
    parser.add_argument("--parse-mode", choices=["rules", "api"], default="rules")
    parser.add_argument("--answer-mode", choices=["template", "api"], default="template")
    parser.add_argument("--model", default=None)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    results = [
        run_case(
            case,
            parse_mode=args.parse_mode,
            answer_mode=args.answer_mode,
            model=args.model,
        )
        for case in cases
    ]

    passed = sum(1 for result in results if result["passed"])
    print(f"Eval result: {passed}/{len(results)} passed")
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"- {status} {result['id']}: {result['input']}")
        for failure in result["failures"]:
            print(f"  - {failure}")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps({"passed": passed, "total": len(results), "results": results}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return 0 if passed == len(results) else 1


def run_case(
    case: dict[str, Any],
    *,
    parse_mode: str,
    answer_mode: str,
    model: str | None,
) -> dict[str, Any]:
    failures: list[str] = []
    actual: dict[str, Any] | None = None

    try:
        actual = run_food_chatbot(
            case["input"],
            parse_mode=parse_mode,
            answer_mode=answer_mode,
            model=model,
            fallback_rules=parse_mode == "api",
            fallback_template=answer_mode == "api",
        )
    except (OpenAIParserError, FinalAnswerError, ValueError, FileNotFoundError) as exc:
        failures.append(f"flow raised {type(exc).__name__}: {exc}")

    if actual is not None:
        failures.extend(check_expectations(case["expect"], actual))

    return {
        "id": case["id"],
        "input": case["input"],
        "passed": not failures,
        "failures": failures,
        "actual": summarize_actual(actual),
    }


def check_expectations(expect: dict[str, Any], actual: dict[str, Any]) -> list[str]:
    task = actual["task"]
    retrieved = actual["retrieved_data"]
    answer = str(actual["answer"])
    failures: list[str] = []

    for key in ["intent", "task_type", "primary_intent", "needs_clarification"]:
        if key in expect and task.get(key) != expect[key]:
            failures.append(f"task.{key}: expected {expect[key]!r}, got {task.get(key)!r}")

    for key, expected_value in expect.get("filters", {}).items():
        actual_value = (task.get("filters") or {}).get(key)
        if actual_value != expected_value:
            failures.append(f"filters.{key}: expected {expected_value!r}, got {actual_value!r}")

    for key, expected_value in expect.get("entities_contains", {}).items():
        actual_value = (task.get("entities") or {}).get(key)
        if isinstance(expected_value, list):
            normalized_actual = [normalize_text(value) for value in as_list(actual_value)]
            for item in expected_value:
                if normalize_text(item) not in normalized_actual:
                    failures.append(f"entities.{key}: missing {item!r} in {actual_value!r}")
        elif actual_value != expected_value:
            failures.append(f"entities.{key}: expected {expected_value!r}, got {actual_value!r}")

    min_questions = expect.get("min_clarifying_questions")
    if min_questions is not None:
        actual_count = len(task.get("clarifying_questions") or [])
        if actual_count < min_questions:
            failures.append(f"clarifying_questions: expected at least {min_questions}, got {actual_count}")

    min_recs = expect.get("min_any_recommendations")
    if min_recs is not None:
        actual_count = any_recommendation_count(retrieved)
        if actual_count < min_recs:
            failures.append(f"recommendations: expected at least {min_recs}, got {actual_count}")

    contains_any = expect.get("answer_contains_any") or []
    if contains_any and not any(normalize_text(fragment) in normalize_text(answer) for fragment in contains_any):
        failures.append(f"answer: expected one of {contains_any!r}, got {answer!r}")

    excludes = expect.get("answer_excludes") or []
    for fragment in excludes:
        if normalize_text(fragment) in normalize_text(answer):
            failures.append(f"answer: should not contain {fragment!r}")

    return failures


def summarize_actual(actual: dict[str, Any] | None) -> dict[str, Any] | None:
    if actual is None:
        return None

    task = actual["task"]
    retrieved = actual["retrieved_data"]
    items = (
        retrieved.get("items")
        or retrieved.get("near_misses")
        or retrieved.get("fallback_items")
        or []
    )
    return {
        "task": {
            "task_type": task.get("task_type"),
            "intent": task.get("intent"),
            "primary_intent": task.get("primary_intent"),
            "entities": task.get("entities"),
            "filters": task.get("filters"),
            "ranking": task.get("ranking"),
            "needs_clarification": task.get("needs_clarification"),
            "clarifying_questions": task.get("clarifying_questions"),
        },
        "recommendation_count": any_recommendation_count(retrieved),
        "top_items": [item.get("item_name") for item in items[:3]],
        "answer": actual.get("answer"),
        "warnings": retrieved.get("warnings", []),
    }


def any_recommendation_count(retrieved: dict[str, Any]) -> int:
    return max(
        len(retrieved.get("items") or []),
        len(retrieved.get("near_misses") or []),
        len(retrieved.get("fallback_items") or []),
    )


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize_text(value: Any) -> str:
    text = str(value).casefold()
    replacements = {
        "à": "a",
        "á": "a",
        "ả": "a",
        "ã": "a",
        "ạ": "a",
        "ă": "a",
        "ằ": "a",
        "ắ": "a",
        "ẳ": "a",
        "ẵ": "a",
        "ặ": "a",
        "â": "a",
        "ầ": "a",
        "ấ": "a",
        "ẩ": "a",
        "ẫ": "a",
        "ậ": "a",
        "đ": "d",
        "è": "e",
        "é": "e",
        "ẻ": "e",
        "ẽ": "e",
        "ẹ": "e",
        "ê": "e",
        "ề": "e",
        "ế": "e",
        "ể": "e",
        "ễ": "e",
        "ệ": "e",
        "ì": "i",
        "í": "i",
        "ỉ": "i",
        "ĩ": "i",
        "ị": "i",
        "ò": "o",
        "ó": "o",
        "ỏ": "o",
        "õ": "o",
        "ọ": "o",
        "ô": "o",
        "ồ": "o",
        "ố": "o",
        "ổ": "o",
        "ỗ": "o",
        "ộ": "o",
        "ơ": "o",
        "ờ": "o",
        "ớ": "o",
        "ở": "o",
        "ỡ": "o",
        "ợ": "o",
        "ù": "u",
        "ú": "u",
        "ủ": "u",
        "ũ": "u",
        "ụ": "u",
        "ư": "u",
        "ừ": "u",
        "ứ": "u",
        "ử": "u",
        "ữ": "u",
        "ự": "u",
        "ỳ": "y",
        "ý": "y",
        "ỷ": "y",
        "ỹ": "y",
        "ỵ": "y",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return " ".join(text.split())


if __name__ == "__main__":
    raise SystemExit(main())
