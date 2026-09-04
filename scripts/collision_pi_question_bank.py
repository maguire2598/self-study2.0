"""Shared expansion for formal Collision & Pi objective question banks."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import TypeVar


OPTION_IDS = ["A", "B", "C", "D"]
ROOT = Path(__file__).resolve().parents[1]

T = TypeVar("T")


SAFE_SECTOR_CONTRACT_COUNT = 18
MOMENTUM_CONTRACT_KEYS = {
    "c4-2-scenario-01", "c4-2-scenario-02", "c4-2-scenario-03",
    "c4-3-scenario-01", "c4-3-scenario-02", "c4-3-scenario-03",
    "c4-3-scenario-04", "c4-4-scenario-01", "c4-4-scenario-02",
    "c4-4-scenario-03", "c4-4-scenario-04", "c4-1-calculation-11",
    "c4-1-concise-05", "c4-2-calculation-12", "c4-2-concise-05",
    "c4-3-calculation-13", "c4-3-concise-05", "c4-4-calculation-14",
    "c4-4-concise-05",
}
MOMENTUM_FIGURE_CONTRACT_KEYS = {
    "c4-2-scenario-02", "c4-2-scenario-03", "c4-2-scenario-04",
    "c4-3-scenario-02", "c4-3-scenario-03", "c4-3-scenario-04",
    "c4-4-scenario-02",
}
VISIBLE_FACT_TOKEN = re.compile(r"\{\{([a-z][a-z0-9_]*)\}\}")
VISIBLE_FACT_FIELDS = {
    "mass_ratio": {"id", "kind", "mass_large", "mass_small"},
    "safe_sector_boundary": {
        "id", "kind", "mass_large", "mass_small", "coefficient", "notation",
    },
    "momentum_value_set": {"id", "kind", "values", "notation"},
    "origin_relation": {"id", "kind", "relation"},
}


def _format_visible_number(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


def _visible_number(value: object, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("visible physics numbers must be numeric, not boolean")
    number = float(value)
    if not math.isfinite(number) or (positive and number <= 0):
        raise ValueError("visible physics number is outside its domain")
    return number


def _render_visible_fact(fact: dict) -> str:
    kind = fact["kind"]
    if kind not in VISIBLE_FACT_FIELDS or set(fact) != VISIBLE_FACT_FIELDS[kind]:
        raise ValueError(f"malformed visible physics fact: {kind}")
    if not isinstance(fact["id"], str) or not re.fullmatch(r"[a-z][a-z0-9_]*", fact["id"]):
        raise ValueError("visible physics fact id is invalid")
    if kind == "mass_ratio":
        _visible_number(fact["mass_large"], positive=True)
        _visible_number(fact["mass_small"], positive=True)
        return f"M/m={_format_visible_number(fact['mass_large'])}/{_format_visible_number(fact['mass_small'])}"
    if kind == "safe_sector_boundary":
        _visible_number(fact["mass_large"], positive=True)
        _visible_number(fact["mass_small"], positive=True)
        _visible_number(fact["coefficient"], positive=True)
        if fact["notation"] not in {"equation", "interval"}:
            raise ValueError("unknown safe-sector notation")
        coefficient = _format_visible_number(fact["coefficient"])
        if fact["notation"] == "equation":
            return f"安全边界为y={coefficient}x"
        return f"安全扇区用0≤y≤{coefficient}x判定"
    if kind == "momentum_value_set":
        values = fact["values"]
        if (not isinstance(values, list) or not values
                or len(values) != len(set(values))):
            raise ValueError("momentum values must be a nonempty unique list")
        for value in values:
            _visible_number(value)
        if fact["notation"] not in {"symbol", "zero_words"}:
            raise ValueError("unknown momentum notation")
        if fact["notation"] == "zero_words":
            if values != [0]:
                raise ValueError("zero_words momentum fact must contain exactly zero")
            return "总动量为零"
        return "和".join(f"P={_format_visible_number(value)}" for value in values)
    if kind == "origin_relation":
        relation = fact["relation"]
        if relation not in {
            "passes_origin", "does_not_pass_origin", "mixed_or_not_asserted",
        }:
            raise ValueError("unknown origin relation")
        if relation == "passes_origin":
            return "零动量线通过原点"
        if relation == "does_not_pass_origin":
            return "非零动量线不通过原点"
        return "图中各动量线不作统一的原点关系断言"
    raise ValueError(f"unknown visible physics fact kind: {kind}")


def render_visible_physics_contract(contract: dict) -> dict[str, str]:
    """Render the prompt and explanation controlled by a visible-fact contract."""
    allowed_contract_fields = {
        "prompt_template", "explanation_template", "facts", "figure_bindings",
    }
    if not {"prompt_template", "explanation_template", "facts"}.issubset(contract):
        raise ValueError("visible physics contract lacks a required field")
    if not set(contract).issubset(allowed_contract_fields):
        raise ValueError("visible physics contract has an unknown field")
    if (not isinstance(contract["prompt_template"], str)
            or not isinstance(contract["explanation_template"], str)
            or not isinstance(contract["facts"], list)
            or not contract["facts"]):
        raise ValueError("visible physics contract fields are malformed")
    for binding in contract.get("figure_bindings", []):
        if set(binding) != {"figure_ref", "momentum_values"}:
            raise ValueError("malformed visible physics figure binding")
        if not isinstance(binding["figure_ref"], str) or not binding["figure_ref"]:
            raise ValueError("visible physics figure reference is malformed")
        values = binding["momentum_values"]
        if (not isinstance(values, list) or not values or len(values) != len(set(values))):
            raise ValueError("visible physics figure momentum values are malformed")
        for value in values:
            _visible_number(value)
    facts = contract.get("facts", [])
    fact_ids = [fact.get("id") for fact in facts]
    if len(fact_ids) != len(set(fact_ids)) or None in fact_ids:
        raise ValueError("visible physics fact ids must be present and unique")
    templates = {
        "prompt": contract.get("prompt_template", ""),
        "explanation": contract.get("explanation_template", ""),
    }
    slots = VISIBLE_FACT_TOKEN.findall("\n".join(templates.values()))
    if sorted(slots) != sorted(fact_ids):
        raise ValueError("each visible physics fact must occupy exactly one known slot")
    rendered = dict(templates)
    for fact in facts:
        token = "{{" + fact["id"] + "}}"
        value = _render_visible_fact(fact)
        rendered = {field: text.replace(token, value) for field, text in rendered.items()}
    if any(VISIBLE_FACT_TOKEN.search(text) for text in rendered.values()):
        raise ValueError("unknown visible physics fact slot")
    return rendered


def _all_source_questions(source: dict) -> list[dict]:
    return [
        question
        for scenario in source["scenarios"]
        for question in scenario["questions"]
    ] + source["standalone_questions"]


def validate_visible_physics_contracts(source: dict) -> None:
    """Validate C using closed facts and exact canonical reconstruction."""
    if source.get("section_id") != "C":
        return
    questions = _all_source_questions(source)
    by_key = {question["key"]: question for question in questions}
    safe_questions = [
        question for question in questions
        if any(
            item["claim"]["kind"] == "safe_sector"
            for item in question.get("answer_contract", {}).get("claims", [])
        )
    ]
    if len(safe_questions) != SAFE_SECTOR_CONTRACT_COUNT:
        raise ValueError("C safe-sector contract population changed")
    required_keys = (
        {question["key"] for question in safe_questions}
        | MOMENTUM_CONTRACT_KEYS | MOMENTUM_FIGURE_CONTRACT_KEYS
    )
    for key in required_keys:
        question = by_key[key]
        contract = question.get("visible_physics_contract")
        if not contract:
            raise ValueError(f"question {key} lacks visible physics contract")
        rendered = render_visible_physics_contract(contract)
        prompt_field = "ask" if "ask" in question else "prompt"
        if rendered["prompt"] != question[prompt_field]:
            raise ValueError(f"question {key} prompt drifted from visible physics facts")
        if rendered["explanation"] != question["explanation"]:
            raise ValueError(f"question {key} explanation drifted from visible physics facts")

    for question in safe_questions:
        facts = question["visible_physics_contract"]["facts"]
        ratios = [fact for fact in facts if fact["kind"] == "mass_ratio"]
        boundaries = [fact for fact in facts if fact["kind"] == "safe_sector_boundary"]
        if len(ratios) != 1 or len(boundaries) != 2:
            raise ValueError(f"question {question['key']} has incomplete safe-sector facts")
        ratio = ratios[0]
        expected = math.sqrt(ratio["mass_small"] / ratio["mass_large"])
        for boundary in boundaries:
            if (boundary["mass_large"], boundary["mass_small"]) != (
                ratio["mass_large"], ratio["mass_small"]
            ) or not math.isclose(boundary["coefficient"], expected):
                raise ValueError(f"question {question['key']} has inconsistent safe boundary")
        for item in question["answer_contract"]["claims"]:
            claim = item["claim"]
            if claim["kind"] == "safe_sector":
                params = claim["parameters"]
                if (params["mass_large"], params["mass_small"]) != (
                    ratio["mass_large"], ratio["mass_small"]
                ) or not math.isclose(params["boundary"], expected):
                    raise ValueError(f"question {question['key']} safe claim disagrees with facts")

    diagram_source = json.loads(
        (ROOT / "content/courses/collision-pi/diagram-source-c.json").read_text(encoding="utf-8")
    )
    diagrams = {diagram["diagram_id"]: diagram for diagram in diagram_source["diagrams"]}
    for key in MOMENTUM_CONTRACT_KEYS | MOMENTUM_FIGURE_CONTRACT_KEYS:
        question = by_key[key]
        contract = question["visible_physics_contract"]
        momentum_facts = [fact for fact in contract["facts"] if fact["kind"] == "momentum_value_set"]
        origins = [fact for fact in contract["facts"] if fact["kind"] == "origin_relation"]
        if key in MOMENTUM_CONTRACT_KEYS and not momentum_facts:
            raise ValueError(f"question {key} lacks a momentum fact")
        if len(origins) != 1:
            raise ValueError(f"question {key} must declare one origin relation")
        bindings = contract.get("figure_bindings", [])
        if key in MOMENTUM_FIGURE_CONTRACT_KEYS and len(bindings) != 1:
            raise ValueError(f"question {key} must bind its momentum figure")
        oracle_values = {
            float(value) for binding in bindings for value in binding["momentum_values"]
        } or {float(value) for fact in momentum_facts for value in fact["values"]}
        expected_origin = (
            "passes_origin" if oracle_values == {0.0}
            else "does_not_pass_origin" if 0.0 not in oracle_values
            else "mixed_or_not_asserted"
        )
        if origins[0]["relation"] != expected_origin:
            raise ValueError(f"question {key} origin relation disagrees with momentum facts")
        for binding in bindings:
            figure_ref = binding["figure_ref"]
            if figure_ref not in question.get("figure_refs", []):
                raise ValueError(f"question {key} binds an unreferenced figure")
            actual = diagrams[figure_ref]["parameters"].get("momentum_values")
            if actual != binding["momentum_values"]:
                raise ValueError(f"question {key} momentum binding disagrees with diagram source")


def content_fingerprint(bank: dict) -> str:
    canonical = {
        key: value for key, value in bank.items() if key != "content_fingerprint"
    }
    payload = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def rotate(values: list[T], offset: int) -> list[T]:
    offset %= len(values)
    return values[offset:] + values[:offset]


def expand_choice_options(
    options: list[dict], offset: int, *, anonymous_figures: bool = False
) -> tuple[list[dict], list[str]]:
    rotated = rotate(options, offset)
    rendered = []
    for index, option in enumerate(rotated):
        option_id = OPTION_IDS[index]
        output = {"id": option_id, "text": option["text"]}
        if anonymous_figures:
            output.update({
                "figure_ref": option["figure_ref"],
                # This field name is deliberately shared with the question-level
                # contract.  Consumers must use it instead of an embedded SVG's
                # title/desc when the same diagram is an anonymous answer option.
                "option_accessibility_label": f"图{option_id}",
                "embedded_figure_aria_hidden": True,
            })
        rendered.append(output)
    answers = [
        OPTION_IDS[index]
        for index, option in enumerate(rotated)
        if option["correct"]
    ]
    return rendered, answers


def expand_questions(source: dict, puzzle: dict, section_id: str) -> list[dict]:
    titles = {
        node["id"]: node["title"]
        for node in puzzle["nodes"]
        if node["board"] == section_id and node["depth"] == 2
    }
    source_items = [
        (scenario, question)
        for scenario in source["scenarios"]
        for question in scenario["questions"]
    ] + [(None, question) for question in source["standalone_questions"]]
    expanded = []
    for index, (scenario, question) in enumerate(source_items):
        node_id = question["node_id"]
        if node_id not in titles:
            raise ValueError(f"question references non-assessed node: {node_id}")
        prompt = question["prompt"] if scenario is None else (
            f"{scenario['context']}\n\n{question['ask']}"
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
                question["options"], index,
                anonymous_figures=question.get("presentation_mode") == "option_figures",
            )
        else:
            item["blanks"] = question["blanks"]
        if "presentation_mode" in question:
            item["presentation_mode"] = question["presentation_mode"]
            item["diagram_focus"] = question.get("diagram_focus", "")
            if "figure_refs" in question:
                item["figure_refs"] = question["figure_refs"]
            if question["presentation_mode"] == "option_figures":
                item["anonymous_option_rendering"] = {
                    "embedded_figure_aria_hidden": True,
                    "accessible_name_source": "option_accessibility_label",
                }
        if "visible_physics_contract" in question:
            contract = copy.deepcopy(question["visible_physics_contract"])
            if scenario is not None:
                contract["prompt_template"] = (
                    f"{scenario['context']}\n\n{contract['prompt_template']}"
                )
            item["visible_physics_contract"] = contract
        expanded.append(item)
    return expanded


def validate_c_figure_references(source: dict) -> None:
    """Reject C references that are not present in the checked-in manifest."""
    if source.get("section_id") != "C":
        return
    manifest_path = ROOT / "content/courses/collision-pi/diagram-manifest-c.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    valid_ids = {diagram["diagram_id"] for diagram in manifest["diagrams"]}
    questions = [
        question
        for scenario in source["scenarios"]
        for question in scenario["questions"]
    ] + source["standalone_questions"]
    for question in questions:
        refs = list(question.get("figure_refs", []))
        refs.extend(
            option["figure_ref"]
            for option in question.get("options", [])
            if "figure_ref" in option
        )
        for figure_ref in refs:
            if figure_ref not in valid_ids:
                raise ValueError(
                    f"question {question['key']} references non-manifest diagram: {figure_ref}"
                )


def build_bank(source: dict, puzzle: dict, *, section_id: str, title: str) -> dict:
    """Build a formal bank from loaded source data after semantic validation."""
    if source["section_id"] != section_id:
        raise ValueError(
            f"source section {source['section_id']} does not match {section_id}"
        )
    validate_c_figure_references(source)
    validate_visible_physics_contracts(source)
    questions = expand_questions(source, puzzle, section_id)
    actual = Counter(question["node_id"] for question in questions)
    expected = Counter(source["node_quotas"])
    if actual != expected:
        raise ValueError(
            f"question quota mismatch: actual={dict(actual)}, expected={dict(expected)}"
        )
    bank = {
        "$schema": "../../../schemas/objective_question_bank.schema.json",
        "course_id": "collision-pi",
        "section_id": section_id,
        "title": title,
        "version": source["version"],
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
    bank["content_fingerprint"] = content_fingerprint(bank)
    return bank


def build_bank_from_paths(
    source_path: Path,
    puzzle_path: Path,
    *,
    section_id: str,
    title: str,
) -> dict:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    puzzle = json.loads(puzzle_path.read_text(encoding="utf-8"))
    return build_bank(source, puzzle, section_id=section_id, title=title)


def write_bank(bank: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(bank, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
