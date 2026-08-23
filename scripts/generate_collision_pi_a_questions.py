"""Expand the reviewed Collision & Pi section A source into the formal bank."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import TypeVar


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "courses" / "collision-pi" / "question-source-a.json"
PUZZLE = ROOT / "content" / "courses" / "collision-pi" / "knowledge-puzzle.json"
OUTPUT = ROOT / "content" / "courses" / "collision-pi" / "question-bank-a.json"
OPTION_IDS = ["A", "B", "C", "D"]

T = TypeVar("T")


def rotate(values: list[T], offset: int) -> list[T]:
    offset %= len(values)
    return values[offset:] + values[:offset]


def load_inputs() -> tuple[dict, dict]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    puzzle = json.loads(PUZZLE.read_text(encoding="utf-8"))
    return source, puzzle


def expand_choice_options(options: list[dict], offset: int) -> tuple[list[dict], list[str]]:
    rotated = rotate(options, offset)
    rendered = [
        {"id": OPTION_IDS[index], "text": option["text"]}
        for index, option in enumerate(rotated)
    ]
    answers = [
        OPTION_IDS[index]
        for index, option in enumerate(rotated)
        if option["correct"]
    ]
    return rendered, answers


def expand_questions(source: dict, puzzle: dict) -> list[dict]:
    titles = {
        node["id"]: node["title"]
        for node in puzzle["nodes"]
        if node["board"] == "A" and node["depth"] == 2
    }
    expanded = []
    source_items = []
    for scenario in source["scenarios"]:
        for question in scenario["questions"]:
            source_items.append((scenario, question))
    for question in source["standalone_questions"]:
        source_items.append((None, question))

    for index, (scenario, question) in enumerate(source_items):
        node_id = question["node_id"]
        if node_id not in titles:
            raise ValueError(f"question references non-assessed node: {node_id}")
        prompt = (
            question["prompt"]
            if scenario is None
            else f"{scenario['context']}\n\n{question['ask']}"
        )
        item = {
            "id": f"cp-{node_id.lower().replace('.', '-')}-{question['key']}",
            "node_id": node_id,
            "node_title": titles[node_id],
            "question_type": question["question_type"],
            "question_style": question["question_style"],
            "assessment_kind": "objective",
            "difficulty": question["difficulty"],
            "prompt": prompt,
            "event_stage": question["event_stage"],
            "variant_axis": question["variant_axis"],
            "explanation": question["explanation"],
            "enabled": True,
            "revision": 0,
            "author_notes": question.get("author_notes", ""),
        }
        if scenario is not None:
            item["scenario_id"] = scenario["id"]
            item["source_refs"] = scenario["source_refs"]
        if question.get("calculation_fixture_id"):
            item["calculation_fixture_id"] = question["calculation_fixture_id"]
        if "options" in question:
            item["options"], item["correct_answers"] = expand_choice_options(
                question["options"], index
            )
        else:
            item["blanks"] = question["blanks"]
        expanded.append(item)
    return expanded


def build_bank() -> dict:
    source, puzzle = load_inputs()
    questions = expand_questions(source, puzzle)
    actual = Counter(question["node_id"] for question in questions)
    expected = Counter(source["node_quotas"])
    if actual != expected:
        raise ValueError(
            f"question quota mismatch: actual={dict(actual)}, expected={dict(expected)}"
        )
    return {
        "$schema": "../../../schemas/objective_question_bank.schema.json",
        "course_id": "collision-pi",
        "section_id": "A",
        "title": "碰撞与π · A板块客观题库",
        "version": "2.0.0",
        "question_count_by_node": source["node_quotas"],
        "delivery_policy": {
            "reveal_answer_after_wrong": False,
            "wrong_answer_action": "error_followup_agent",
            "correct_answer_actions": ["next_question", "error_followup_agent"],
        },
        "status_assessment": {
            "enabled": False,
            "note": "按当前产品决定暂缓设计和生成。",
        },
        "questions": questions,
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    bank = build_bank()
    OUTPUT.write_text(
        json.dumps(bank, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"generated {len(bank['questions'])} questions -> {OUTPUT}")


if __name__ == "__main__":
    main()
