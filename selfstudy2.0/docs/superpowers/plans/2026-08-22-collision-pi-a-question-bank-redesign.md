# Collision Pi A Question Bank Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the uniform 192-question A bank with a 27-node, 140-question scenario bank that supports linked event stages, eight verified calculation questions, and incline/spring extensions.

**Architecture:** Keep `knowledge-puzzle.json` as the node source of truth and add `question-source-a.json` as the authored question source. Deterministic Python builders expand scenario contexts into self-contained bank questions, render the knowledge-puzzle Markdown, and embed the bank in the author editor. Tests enforce node quotas, style ratios, physics fixtures, schema fields, build reproducibility, and browser filtering.

**Tech Stack:** Python 3.13 standard library, JSON Schema 2020-12, HTML/CSS/vanilla JavaScript, Node.js validation, Python `unittest`.

**Spec:** `docs/superpowers/specs/2026-08-22-collision-pi-a-question-bank-redesign.md`

## Global Constraints

- Use the approved node counts exactly: A 27, B 30, C 46, D 36, total 139.
- A contains exactly 7 depth-1 stage nodes and 20 depth-2 assessed nodes.
- Generate exactly 140 objective questions and use the per-node quotas from the spec.
- Use exactly 88 `scenario`, 8 `calculation`, and 44 `concise` questions. Scenario plus calculation therefore equals 96 of 140 questions, above the 65% requirement.
- Use exactly 10 core scenario families across A3/A4/A5 and exactly 3 extension families in A7.
- Every final scenario question repeats enough context to stand alone.
- Do not generate prompts shaped like `关于“节点标题”`、`判断“节点标题”` or `下列哪项最符合“节点标题”`.
- Keep all questions objective. Do not generate status-observation questions.
- Keep correct answers and explanations in author/judging artifacts only; do not add a student delivery surface.
- Keep `reveal_answer_after_wrong=false` and `wrong_answer_action=error_followup_agent`.
- Use `sources/theory/弹性碰撞与π.txt` as the course source. Cross-check collision formulas against OpenStax 8.4, incline energy against OpenStax 7.3, and spring energy against OpenStax 7.4.
- Record source conflicts in `author_notes`; do not silently rewrite the source video as wrong.
- Use UTF-8 for every generated JSON, Markdown, and HTML artifact.
- Before Task 1, invoke `superpowers:using-git-worktrees` and execute the plan in an isolated `codex/` worktree unless the executor is already in an isolated worktree.

## File Map

**Create:**

- `content/courses/collision-pi/question-source-a.json`: authored scenario catalog, standalone questions, quotas, references, and calculation fixtures.
- `schemas/objective_question_source.schema.json`: author-source contract.
- `scripts/build_collision_pi_knowledge_puzzle.py`: render `knowledge-puzzle.md` from the JSON source of truth.
- `tests/test_question_source.py`: source counts, scenario families, style distribution, banned prompt forms, and physics calculations.

**Modify:**

- `content/courses/collision-pi/knowledge-puzzle.json`: replace the old A nodes with the approved 27-node structure and bump version to `2.0.0`.
- `content/courses/collision-pi/knowledge-puzzle.md`: generated 139-node directory.
- `scripts/generate_collision_pi_a_questions.py`: load source JSON and expand deterministic questions.
- `content/courses/collision-pi/question-bank-a.json`: generated 140-question bank version `2.0.0`.
- `schemas/objective_question_bank.schema.json`: 140-item limit and scenario metadata.
- `tests/test_knowledge_puzzle.py`, `tests/test_question_bank.py`, `tests/test_project_contract.py`: new contracts.
- `authoring/collision-pi-question-editor.template.html`: scenario metadata and scenario-family filtering.
- `authoring/collision-pi-question-editor.html`: generated editor.
- `scripts/validate_question_editor.js`: 140-question and scenario-filter validation.
- `AGENTS.md`, `README.md`, `docs/roadmap.md`, `docs/decisions/conversation-decisions.md`: replace the old 144/32/192/uniform-six facts.

**Delete:**

- `scripts/import_knowledge_puzzle.py`: the one-time legacy importer depends on the retired 144-node selector contract. The new builder reads the current JSON directly.

## Source Baselines

Use these stable source IDs in `question-source-a.json`:

| Source ID | Location | Scope |
| --- | --- | --- |
| `video-main` | `sources/theory/弹性碰撞与π.txt` | Course narrative, collision-and-π setup, learning sequence |
| `openstax-collision` | `https://openstax.org/books/college-physics/pages/8-4-elastic-collisions-in-one-dimension` | One-dimensional elastic collision, momentum and kinetic-energy equations |
| `openstax-inelastic` | `https://openstax.org/books/physics/pages/8-3-elastic-and-inelastic-collisions` | Elastic/inelastic distinction and system momentum conditions |
| `openstax-incline` | `https://openstax.org/books/college-physics-2e/pages/7-3-gravitational-potential-energy` | Gravitational potential energy and speed from height |
| `openstax-spring` | `https://openstax.org/books/college-physics-2e/pages/7-4-conservative-forces-and-potential-energy` | Hooke-law spring energy and staged energy calculations |

The local source has compressed or ambiguous algebra around lines 14-15. Preserve its instructional intent, but generate numerical answers from the independently checked equations in Tasks 2 and 3. Add an `author_notes` warning to any question whose wording touches the wall-as-infinite-mass analogy.

---

### Task 1: Replace the A Node Contract and Add a Markdown Builder

**Files:**

- Create: `scripts/build_collision_pi_knowledge_puzzle.py`
- Modify: `content/courses/collision-pi/knowledge-puzzle.json:1-263`
- Modify: `content/courses/collision-pi/knowledge-puzzle.md:1-38`
- Modify: `tests/test_knowledge_puzzle.py:11-47`
- Modify: `tests/test_project_contract.py:26-32`
- Delete: `scripts/import_knowledge_puzzle.py`

**Interfaces:**

- Consumes: `content/courses/collision-pi/knowledge-puzzle.json` with `course_id`, `version`, and `nodes`.
- Produces: `render_markdown(puzzle: dict) -> str` and a generated `knowledge-puzzle.md` whose A node IDs are exactly `A1`, `A1.1` through `A1.3`, `A2`, `A2.1` through `A2.2`, `A3`, `A3.1` through `A3.5`, `A4`, `A4.1` through `A4.3`, `A5`, `A5.1` through `A5.2`, `A6`, `A6.1` through `A6.2`, `A7`, `A7.1` through `A7.3`.

- [ ] **Step 1: Write failing node and renderer tests**

Replace the fixed-count test and add hierarchy/rendering tests:

```python
def test_exact_node_and_board_counts(self):
    self.assertEqual(len(self.nodes), 139)
    self.assertEqual(
        Counter(node["board"] for node in self.nodes),
        Counter({"A": 27, "B": 30, "C": 46, "D": 36}),
    )

def test_a_has_seven_stages_and_twenty_assessed_nodes(self):
    a_nodes = [node for node in self.nodes if node["board"] == "A"]
    self.assertEqual(sum(node["depth"] == 1 for node in a_nodes), 7)
    self.assertEqual(sum(node["depth"] == 2 for node in a_nodes), 20)
    self.assertEqual(
        [node["id"] for node in a_nodes if node["depth"] == 1],
        ["A1", "A2", "A3", "A4", "A5", "A6", "A7"],
    )

def test_markdown_is_generated_from_json(self):
    from scripts.build_collision_pi_knowledge_puzzle import render_markdown
    expected = PUZZLE_PATH.with_suffix(".md").read_text(encoding="utf-8")
    self.assertEqual(render_markdown(self.puzzle), expected)
```

- [ ] **Step 2: Run the focused tests and verify the expected failure**

Run:

```powershell
python -m unittest tests.test_knowledge_puzzle tests.test_project_contract -v
```

Expected: FAIL because the current puzzle still has 144 nodes, A still has 32 nodes, and the new builder module does not exist.

- [ ] **Step 3: Replace the A node array and implement the renderer**

Copy the 27 exact node titles, roles, and summaries from the spec table into the A segment of `knowledge-puzzle.json`; preserve every B/C/D object byte-for-byte apart from surrounding JSON formatting. Set puzzle version to `2.0.0`.

Implement the builder:

```python
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUZZLE = ROOT / "content" / "courses" / "collision-pi" / "knowledge-puzzle.json"
OUTPUT = PUZZLE.with_suffix(".md")
BOARD_TITLES = {
    "A": "碰撞现象与结论",
    "B": "现象与原理",
    "C": "几何化",
    "D": "从模型到π与位数关系",
}


def render_markdown(puzzle: dict) -> str:
    lines = [
        "# 碰撞与π知识拼图",
        "",
        "> 本目录由 `knowledge-puzzle.json` 生成；JSON 是节点单一真相来源。",
        "",
    ]
    for board, title in BOARD_TITLES.items():
        lines.extend([f"## [{board}] {title}", ""])
        for node in (item for item in puzzle["nodes"] if item["board"] == board):
            indent = "  " if node["depth"] == 2 else ""
            role = f" · {node['role']}" if node["role"] != "核心" else ""
            lines.append(f"{indent}- **{node['id']} {node['title']}**{role}：{node['summary']}")
        lines.append("")
    lines.extend([
        "> C9 光线反射法为选修内容。",
        "",
        "> **文档版本**：2.0.0",
        "> **生成日期**：2026-08-22",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    puzzle = json.loads(PUZZLE.read_text(encoding="utf-8"))
    OUTPUT.write_text(render_markdown(puzzle), encoding="utf-8")
    print(f"built knowledge puzzle markdown with {len(puzzle['nodes'])} nodes")


if __name__ == "__main__":
    main()
```

Delete `scripts/import_knowledge_puzzle.py`, then run:

```powershell
python scripts/build_collision_pi_knowledge_puzzle.py
```

- [ ] **Step 4: Run focused tests and verify green**

Run:

```powershell
python -m unittest tests.test_knowledge_puzzle tests.test_project_contract -v
```

Expected: all knowledge-puzzle and project-contract tests pass. The project-contract question assertion still expects the unchanged 192-question bank until Task 3.

- [ ] **Step 5: Commit the node model**

```powershell
git add content/courses/collision-pi/knowledge-puzzle.json content/courses/collision-pi/knowledge-puzzle.md scripts/build_collision_pi_knowledge_puzzle.py scripts/import_knowledge_puzzle.py tests/test_knowledge_puzzle.py tests/test_project_contract.py
git commit -m "feat: consolidate collision pi A nodes"
```

---

### Task 2: Add the Authored Question Source and Physics Fixtures

**Files:**

- Create: `content/courses/collision-pi/question-source-a.json`
- Create: `schemas/objective_question_source.schema.json`
- Create: `tests/test_question_source.py`

**Interfaces:**

- Consumes: the 20 depth-2 A nodes from Task 1 and the five source IDs in `Source Baselines`.
- Produces: a version `2.0.0` source document with `node_quotas: dict[str, int]`, `source_catalog: list[dict]`, `calculation_fixtures: list[dict]`, `scenarios: list[dict]`, and `standalone_questions: list[dict]`.
- Each scenario question has `key`, `node_id`, `question_type`, `question_style`, `difficulty`, `event_stage`, `variant_axis`, `ask`, answer data, `explanation`, and optional `author_notes`. `difficulty` is an integer from 1 through 3.
- Each standalone question has the same fields, including `difficulty`, but uses `prompt` instead of `ask` and omits `scenario_id`.

- [ ] **Step 1: Write failing source-contract tests**

Create `tests/test_question_source.py` with these assertions:

```python
import json
import math
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content/courses/collision-pi/question-source-a.json"

EXPECTED_QUOTAS = {
    "A1.1": 5, "A1.2": 5, "A1.3": 4,
    "A2.1": 6, "A2.2": 5,
    "A3.1": 8, "A3.2": 10, "A3.3": 12, "A3.4": 8, "A3.5": 10,
    "A4.1": 6, "A4.2": 10, "A4.3": 8,
    "A5.1": 10, "A5.2": 4,
    "A6.1": 10, "A6.2": 5,
    "A7.1": 5, "A7.2": 5, "A7.3": 4,
}
CORE_SCENARIOS = {
    "SC-A3-RELATIVE", "SC-A3-EQUAL", "SC-A3-UNEQUAL", "SC-A3-LARGE-RATIO",
    "SC-A3-NONIDEAL", "SC-A3-CONSERVATION", "SC-A4-FIRST-WALL",
    "SC-A4-CHASE", "SC-A4-STATE-1", "SC-A4-STATE-3",
}
EXTENSION_SCENARIOS = {"SC-A7-INCLINE", "SC-A7-SPRING", "SC-A7-BOUNDARY"}


class QuestionSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.scenario_questions = [
            question
            for scenario in cls.source["scenarios"]
            for question in scenario["questions"]
        ]
        cls.standalone = cls.source["standalone_questions"]

    def test_quota_and_scenario_contract(self):
        self.assertEqual(self.source["node_quotas"], EXPECTED_QUOTAS)
        self.assertEqual(sum(EXPECTED_QUOTAS.values()), 140)
        scenario_ids = {scenario["id"] for scenario in self.source["scenarios"]}
        self.assertEqual(scenario_ids, CORE_SCENARIOS | EXTENSION_SCENARIOS)
        self.assertEqual(len(self.scenario_questions), 96)
        self.assertEqual(len(self.standalone), 44)

    def test_style_distribution(self):
        styles = Counter(
            question["question_style"]
            for question in self.scenario_questions + self.standalone
        )
        self.assertEqual(styles, Counter({"scenario": 88, "calculation": 8, "concise": 44}))

    def test_calculation_fixtures_are_physically_consistent(self):
        fixtures = self.source["calculation_fixtures"]
        self.assertEqual(len(fixtures), 8)
        for fixture in fixtures:
            if fixture["kind"] == "elastic_1d":
                m1, m2 = fixture["m1"], fixture["m2"]
                u1, u2 = fixture["u1"], fixture["u2"]
                v1 = ((m1 - m2) * u1 + 2 * m2 * u2) / (m1 + m2)
                v2 = (2 * m1 * u1 + (m2 - m1) * u2) / (m1 + m2)
                self.assertAlmostEqual(v1, fixture["expected"]["v1"])
                self.assertAlmostEqual(v2, fixture["expected"]["v2"])
                self.assertAlmostEqual(m1 * u1 + m2 * u2, m1 * v1 + m2 * v2)
                self.assertAlmostEqual(
                    0.5 * m1 * u1 ** 2 + 0.5 * m2 * u2 ** 2,
                    0.5 * m1 * v1 ** 2 + 0.5 * m2 * v2 ** 2,
                )
                if "delta_p1" in fixture["expected"]:
                    self.assertAlmostEqual(m1 * (v1 - u1), fixture["expected"]["delta_p1"])
                    self.assertAlmostEqual(m2 * (v2 - u2), fixture["expected"]["delta_p2"])
            elif fixture["kind"] == "incline_speed":
                self.assertAlmostEqual(
                    math.sqrt(2 * fixture["g"] * fixture["height"]),
                    fixture["expected"]["speed"],
                )
            elif fixture["kind"] == "spring_compression":
                expected = fixture["speed"] * math.sqrt(fixture["mass"] / fixture["k"])
                self.assertAlmostEqual(expected, fixture["expected"]["compression"])
            else:
                self.fail(f"unknown calculation kind: {fixture['kind']}")
```

Add these source-shape tests to the same class:

```python
    def test_sources_and_question_keys_are_complete(self):
        expected_sources = {
            "video-main", "openstax-collision", "openstax-inelastic",
            "openstax-incline", "openstax-spring",
        }
        self.assertEqual({item["id"] for item in self.source["source_catalog"]}, expected_sources)
        for scenario in self.source["scenarios"]:
            keys = [question["key"] for question in scenario["questions"]]
            self.assertEqual(len(keys), len(set(keys)), scenario["id"])
            self.assertTrue(set(scenario["source_refs"]).issubset(expected_sources))

    def test_question_payloads_match_types_and_style(self):
        banned = ("关于“", "判断“", "下列哪项最符合“")
        fixture_ids = {fixture["id"] for fixture in self.source["calculation_fixtures"]}
        for question in self.scenario_questions + self.standalone:
            text = question.get("ask", question.get("prompt", ""))
            self.assertTrue(text.strip())
            self.assertFalse(any(phrase in text for phrase in banned), text)
            self.assertIn(question["difficulty"], {1, 2, 3})
            if question["question_type"] in {"single_choice", "multiple_choice"}:
                self.assertEqual(len(question["options"]), 4)
                correct = sum(option["correct"] for option in question["options"])
                self.assertEqual(correct, 1 if question["question_type"] == "single_choice" else 2)
            else:
                self.assertTrue(question["blanks"])
                self.assertTrue(all(blank["accepted_answers"] for blank in question["blanks"]))
            if question["question_style"] == "calculation":
                self.assertIn(question["calculation_fixture_id"], fixture_ids)

    def test_scenario_questions_are_self_contained(self):
        dependent_phrases = ("根据上一问", "由前题可知", "继续上题", "沿用上一题")
        for scenario in self.source["scenarios"]:
            self.assertTrue(scenario["context"].strip())
            for question in scenario["questions"]:
                self.assertFalse(any(phrase in question["ask"] for phrase in dependent_phrases))
```

- [ ] **Step 2: Run the source test and verify red**

Run:

```powershell
python -m unittest tests.test_question_source -v
```

Expected: ERROR because `question-source-a.json` does not exist.

- [ ] **Step 3: Create the source schema**

Define these required top-level fields in `schemas/objective_question_source.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ObjectiveQuestionSource",
  "type": "object",
  "required": [
    "course_id", "section_id", "version", "node_quotas", "source_catalog",
    "calculation_fixtures", "scenarios", "standalone_questions"
  ],
  "properties": {
    "course_id": { "const": "collision-pi" },
    "section_id": { "const": "A" },
    "version": { "const": "2.0.0" },
    "node_quotas": { "type": "object", "minProperties": 20, "maxProperties": 20 },
    "source_catalog": { "type": "array", "minItems": 5 },
    "calculation_fixtures": { "type": "array", "minItems": 8, "maxItems": 8 },
    "scenarios": { "type": "array", "minItems": 13, "maxItems": 13 },
    "standalone_questions": { "type": "array", "minItems": 44, "maxItems": 44 }
  }
}
```

Add nested item schemas that require the interface fields listed above. Restrict `question_style` to `scenario`, `calculation`, or `concise`; restrict `event_stage` to the seven values in the spec; restrict `question_type` to the three existing objective types.

Use these exact reusable definitions and reference them from `scenarios[].questions[]` and `standalone_questions[]`:

```json
"$defs": {
  "option": {
    "type": "object",
    "required": ["text", "correct"],
    "properties": {
      "text": {"type": "string", "minLength": 1},
      "correct": {"type": "boolean"}
    }
  },
  "blank": {
    "type": "object",
    "required": ["id", "accepted_answers"],
    "properties": {
      "id": {"type": "string", "minLength": 1},
      "accepted_answers": {
        "type": "array",
        "minItems": 1,
        "items": {"type": "string", "minLength": 1}
      }
    }
  },
  "question": {
    "type": "object",
    "required": [
      "key", "node_id", "question_type", "question_style", "difficulty",
      "event_stage", "variant_axis", "explanation"
    ],
    "properties": {
      "key": {"type": "string", "minLength": 1},
      "node_id": {"type": "string", "pattern": "^A[1-7]\\.[1-5]$"},
      "question_type": {"enum": ["single_choice", "multiple_choice", "multi_blank"]},
      "question_style": {"enum": ["scenario", "calculation", "concise"]},
      "difficulty": {"type": "integer", "minimum": 1, "maximum": 3},
      "event_stage": {
        "enum": [
          "initial", "after_first_collision", "after_wall_collision",
          "after_second_collision", "terminal", "special_case", "extension_stage"
        ]
      },
      "variant_axis": {
        "enum": [
          "mass_ratio", "initial_velocity", "friction", "elasticity", "incline",
          "spring", "system_boundary", "counting", "direction", "observation",
          "model_assumption", "event_sequence"
        ]
      },
      "prompt": {"type": "string", "minLength": 1},
      "ask": {"type": "string", "minLength": 1},
      "options": {"type": "array", "minItems": 4, "maxItems": 4, "items": {"$ref": "#/$defs/option"}},
      "blanks": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/blank"}},
      "calculation_fixture_id": {"type": "string"},
      "explanation": {"type": "string", "minLength": 1},
      "author_notes": {"type": "string"}
    }
  },
  "scenario": {
    "type": "object",
    "required": ["id", "context", "source_refs", "questions"],
    "properties": {
      "id": {"type": "string", "pattern": "^SC-A[347]-"},
      "context": {"type": "string", "minLength": 1},
      "source_refs": {"type": "array", "minItems": 1, "items": {"type": "string"}},
      "questions": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/question"}}
    }
  }
}
```

Set `scenarios.items` to `{"$ref": "#/$defs/scenario"}` and `standalone_questions.items` to `{"$ref": "#/$defs/question"}`. Source tests enforce that scenario entries use `ask`, standalone entries use `prompt`, and choice/blank payloads match `question_type`.

- [ ] **Step 4: Author the exact scenario catalog and standalone coverage**

Create `question-source-a.json` with this exact family allocation:

| Scenario | Question allocation | Physical context |
| --- | --- | --- |
| `SC-A3-RELATIVE` | A3.1 × 8 | Left/right positions and four relative-velocity patterns |
| `SC-A3-EQUAL` | A3.2 × 10 | Equal masses, elastic collision, one stationary or head-on |
| `SC-A3-UNEQUAL` | A3.3 × 8 | `M=3m`, `uM=-4 m/s`, `um=0`, plus one moving-target variant |
| `SC-A3-LARGE-RATIO` | A3.3 × 4 | `M/m=100`, qualitative speed and energy trends |
| `SC-A3-NONIDEAL` | A3.4 × 8 | Same initial state under elastic, perfectly inelastic, friction/no-friction variants |
| `SC-A3-CONSERVATION` | A3.5 × 10 | Single-body momentum/energy changes versus system totals |
| `SC-A4-FIRST-WALL` | A4.1 × 6 | First collision sends the small block toward the wall |
| `SC-A4-CHASE` | A4.2 × 10 and A5.1 × 5 | Wall reflection, catch-up, and terminal comparisons |
| `SC-A4-STATE-1` | A4.3 × 4 | Equal-mass event table through the second block collision |
| `SC-A4-STATE-3` | A4.3 × 4 and A5.1 × 5 | `M=3m` event table and terminal-state checks |
| `SC-A7-INCLINE` | A7.1 × 5 | Smooth incline to horizontal track, then a short collision |
| `SC-A7-SPRING` | A7.2 × 5 | Short collision followed by spring compression |
| `SC-A7-BOUNDARY` | A7.3 × 4 | Choose the system and conservation law separately for each stage |

The 44 standalone questions cover A1.1 × 5, A1.2 × 5, A1.3 × 4, A2.1 × 6, A2.2 × 5, A5.2 × 4, A6.1 × 10, and A6.2 × 5.

Use this canonical scenario shape:

```json
{
  "id": "SC-A3-EQUAL",
  "context": "光滑水平面上，取向右为正。质量相同的大物块 M 在小物块 m 的右侧，以速度 -V 向左运动，小物块初始静止；两物块发生一维完全弹性碰撞。",
  "source_refs": ["video-main", "openstax-collision"],
  "questions": [
    {
      "key": "first-collision-velocity",
      "node_id": "A3.2",
      "question_type": "single_choice",
      "question_style": "scenario",
      "event_stage": "after_first_collision",
      "variant_axis": "mass_ratio",
      "ask": "第一次碰撞后，两物块的速度分别是多少？",
      "options": [
        {"text": "vM=0，vm=-V", "correct": true},
        {"text": "vM=-V，vm=0", "correct": false},
        {"text": "vM=0，vm=V", "correct": false},
        {"text": "vM=-V/2，vm=-V/2", "correct": false}
      ],
      "explanation": "等质量一维完全弹性碰撞交换速度，因此大物块停下，小物块取得 -V。",
      "author_notes": ""
    }
  ]
}
```

Write every scenario question so `context + ask` is a complete prompt. Do not write `根据上一问`、`由前题可知`、`继续上题` or equivalent dependencies.

- [ ] **Step 5: Add the eight exact calculation fixtures and questions**

Use these fixture inputs and expected results:

| Fixture | Node | Kind | Inputs | Expected |
| --- | --- | --- | --- | --- |
| `CAL-A3-EQ-01` | A3.2 | elastic_1d | `m1=2,m2=2,u1=-3,u2=0` | `v1=0,v2=-3` |
| `CAL-A3-EQ-02` | A3.2 | elastic_1d | `m1=1,m2=1,u1=2,u2=-1` | `v1=-1,v2=2` |
| `CAL-A3-UN-01` | A3.3 | elastic_1d | `m1=3,m2=1,u1=-4,u2=0` | `v1=-2,v2=-6` |
| `CAL-A3-UN-02` | A3.3 | elastic_1d | `m1=1,m2=3,u1=4,u2=0` | `v1=-2,v2=2` |
| `CAL-A3-UN-03` | A3.3 | elastic_1d | `m1=3,m2=1,u1=2,u2=-2` | `v1=0,v2=4` |
| `CAL-A3-DP-01` | A3.5 | elastic_1d | `m1=3,m2=1,u1=-4,u2=0` | `v1=-2,v2=-6,delta_p1=6,delta_p2=-6` |
| `CAL-A7-IN-01` | A7.1 | incline_speed | `g=10,height=1.25` | `speed=5` |
| `CAL-A7-SP-01` | A7.2 | spring_compression | `mass=1,speed=2,k=100` | `compression=0.2` |

Link exactly one `question_style=calculation` question to each fixture through `calculation_fixture_id`. Calculation prompts must state units and direction conventions.

- [ ] **Step 6: Run source tests and verify green**

Run:

```powershell
python -m unittest tests.test_question_source -v
```

Expected: all source, scenario, style, banned-copy, and physics-fixture tests pass.

- [ ] **Step 7: Commit the authored source**

```powershell
git add content/courses/collision-pi/question-source-a.json schemas/objective_question_source.schema.json tests/test_question_source.py
git commit -m "feat: author scenario source for A question bank"
```

---

### Task 3: Replace the Generic Generator and Update the Bank Contract

**Files:**

- Modify: `scripts/generate_collision_pi_a_questions.py:1-268`
- Modify: `schemas/objective_question_bank.schema.json:1-76`
- Modify: `tests/test_question_bank.py:1-64`
- Modify: `tests/test_project_contract.py:34-42`
- Generate: `content/courses/collision-pi/question-bank-a.json`

**Interfaces:**

- Consumes: `question-source-a.json`, `knowledge-puzzle.json`, and the source question shapes from Task 2.
- Produces: `load_inputs() -> tuple[dict, dict]`, `expand_questions(source: dict, puzzle: dict) -> list[dict]`, and `build_bank() -> dict`.
- Bank metadata includes `version="2.0.0"` and `question_count_by_node` equal to `node_quotas`.

- [ ] **Step 1: Write failing bank-generation tests**

Replace the uniform distribution test with:

```python
EXPECTED_QUOTAS = {
    "A1.1": 5, "A1.2": 5, "A1.3": 4,
    "A2.1": 6, "A2.2": 5,
    "A3.1": 8, "A3.2": 10, "A3.3": 12, "A3.4": 8, "A3.5": 10,
    "A4.1": 6, "A4.2": 10, "A4.3": 8,
    "A5.1": 10, "A5.2": 4,
    "A6.1": 10, "A6.2": 5,
    "A7.1": 5, "A7.2": 5, "A7.3": 4,
}

def test_exact_question_count_and_node_distribution(self):
    self.assertEqual(len(self.questions), 140)
    self.assertEqual(self.bank["question_count_by_node"], EXPECTED_QUOTAS)
    self.assertEqual(Counter(q["node_id"] for q in self.questions), Counter(EXPECTED_QUOTAS))
    self.assertGreater(len(set(EXPECTED_QUOTAS.values())), 1)

def test_bank_nodes_equal_assessed_a_nodes(self):
    puzzle = json.loads(PUZZLE_PATH.read_text(encoding="utf-8"))
    expected = {
        node["id"] for node in puzzle["nodes"]
        if node["board"] == "A" and node["depth"] == 2
    }
    self.assertEqual({q["node_id"] for q in self.questions}, expected)

def test_style_and_scenario_contract(self):
    styles = Counter(q["question_style"] for q in self.questions)
    self.assertEqual(styles, Counter({"scenario": 88, "calculation": 8, "concise": 44}))
    self.assertEqual(len({q["scenario_id"] for q in self.questions if q.get("scenario_id")}), 13)
    self.assertTrue(all(q.get("calculation_fixture_id") for q in self.questions if q["question_style"] == "calculation"))
```

Add banned prompt checks and assert that `node_title` equals the current puzzle title for every question.

- [ ] **Step 2: Run the generator tests and verify red**

Run:

```powershell
python -m unittest tests.test_question_bank tests.test_project_contract -v
```

Expected: FAIL because the current bank has 192 questions, uses the old nodes, and lacks `question_style` and scenario fields.

- [ ] **Step 3: Implement deterministic source expansion**

Replace `NODE_SPECS` and `make_questions` with functions shaped as follows:

```python
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "courses" / "collision-pi" / "question-source-a.json"
PUZZLE = ROOT / "content" / "courses" / "collision-pi" / "knowledge-puzzle.json"
OUTPUT = ROOT / "content" / "courses" / "collision-pi" / "question-bank-a.json"
OPTION_IDS = ["A", "B", "C", "D"]


def load_inputs() -> tuple[dict, dict]:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    puzzle = json.loads(PUZZLE.read_text(encoding="utf-8"))
    return source, puzzle


def expand_choice_options(options: list[dict], offset: int) -> tuple[list[dict], list[str]]:
    rotated = rotate(options, offset)
    rendered = [{"id": OPTION_IDS[index], "text": option["text"]} for index, option in enumerate(rotated)]
    answers = [OPTION_IDS[index] for index, option in enumerate(rotated) if option["correct"]]
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
        prompt = question["prompt"] if scenario is None else f"{scenario['context']}\n\n{question['ask']}"
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
            item["options"], item["correct_answers"] = expand_choice_options(question["options"], index)
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
        raise ValueError(f"question quota mismatch: actual={dict(actual)}, expected={dict(expected)}")
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
```

Import `Counter` from `collections`. Keep `main()` as the UTF-8 JSON writer and print the generated question count.

- [ ] **Step 4: Update the formal bank schema**

Set `minItems` and `maxItems` to 140. Add `question_style` to required fields and define:

```json
"question_style": { "enum": ["scenario", "calculation", "concise"] },
"scenario_id": { "type": "string" },
"event_stage": {
  "enum": [
    "initial", "after_first_collision", "after_wall_collision",
    "after_second_collision", "terminal", "special_case", "extension_stage"
  ]
},
"variant_axis": {
  "enum": [
    "mass_ratio", "initial_velocity", "friction", "elasticity", "incline", "spring",
    "system_boundary", "counting", "direction", "observation", "model_assumption", "event_sequence"
  ]
},
"calculation_fixture_id": { "type": "string" },
"source_refs": { "type": "array", "items": { "type": "string" } }
```

Add `question_count_by_node` as a required top-level object with exactly 20 properties. Remove the retired `distribution_per_node` contract from generated data.

- [ ] **Step 5: Generate the bank and verify green**

Run:

```powershell
python scripts/generate_collision_pi_a_questions.py
python -m unittest tests.test_question_source tests.test_question_bank tests.test_project_contract -v
```

Expected: generated 140 questions; all source, bank, and project contract tests pass.

- [ ] **Step 6: Commit the generator and bank**

```powershell
git add scripts/generate_collision_pi_a_questions.py schemas/objective_question_bank.schema.json content/courses/collision-pi/question-bank-a.json tests/test_question_bank.py tests/test_project_contract.py
git commit -m "feat: generate the 140-question A scenario bank"
```

---

### Task 4: Upgrade the Author Filter for Scenario Families

**Files:**

- Modify: `authoring/collision-pi-question-editor.template.html:1-277`
- Modify: `scripts/validate_question_editor.js:1-20`
- Generate: `authoring/collision-pi-question-editor.html`
- Test: `scripts/validate_question_editor.js`

**Interfaces:**

- Consumes: the version `2.0.0` bank from Task 3.
- Produces: a scenario filter `#questionScenarioFilter`; visible metadata labels for `question_style`, `scenario_id`, and `event_stage`; filtering by node, type, scenario, and keyword.

- [ ] **Step 1: Strengthen the validator before editing the template**

Update `scripts/validate_question_editor.js` to assert the new count and controls:

```javascript
if (bank.questions.length !== 140) {
  throw new Error(`expected 140 questions, found ${bank.questions.length}`);
}
if (!source.includes('id="questionScenarioFilter"')) {
  throw new Error('scenario filter is missing');
}
if (!source.includes('question.scenario_id') || !source.includes('question.question_style')) {
  throw new Error('scenario metadata rendering is missing');
}
```

- [ ] **Step 2: Run the validator and verify red**

Run:

```powershell
node scripts/validate_question_editor.js
```

Expected: FAIL because the generated editor still contains 192 questions and no scenario filter.

- [ ] **Step 3: Add scenario filtering and metadata rendering**

Add this control next to node and type:

```html
<label class="form-label">场景题组
  <select class="form-select" id="questionScenarioFilter">
    <option value="all">全部场景</option>
    <option value="standalone">独立短题</option>
  </select>
</label>
```

Build scenario options from unique `scenario_id` values and update filtering:

```javascript
const scenarioFilter = root.querySelector('#questionScenarioFilter');
const scenarios = [...new Set(bank.questions.map(question => question.scenario_id).filter(Boolean))];

scenarios.forEach(scenarioId => {
  const option = document.createElement('option');
  option.value = scenarioId;
  option.textContent = scenarioId;
  scenarioFilter.append(option);
});

function matchesScenario(question) {
  if (scenarioFilter.value === 'all') return true;
  if (scenarioFilter.value === 'standalone') return !question.scenario_id;
  return question.scenario_id === scenarioFilter.value;
}
```

Add `matchesScenario(question)` to `render()` and register `scenarioFilter.addEventListener('change', render)`.

In `renderQuestion()`, append a metadata line before the prompt:

```javascript
const metadata = document.createElement('p');
metadata.className = 'text-small text-muted';
metadata.textContent = [
  question.question_style,
  question.scenario_id || 'standalone',
  question.event_stage
].join(' · ');
card.append(metadata);
```

- [ ] **Step 4: Rebuild and run the static validator**

Run:

```powershell
python scripts/build_collision_pi_question_editor.py
node scripts/validate_question_editor.js
```

Expected: `question editor validation OK: 140 questions, 2 script blocks`.

- [ ] **Step 5: Commit the author filter**

```powershell
git add authoring/collision-pi-question-editor.template.html authoring/collision-pi-question-editor.html scripts/validate_question_editor.js
git commit -m "feat: filter A questions by scenario family"
```

---

### Task 5: Update Project Facts and Run End-to-End Verification

**Files:**

- Modify: `AGENTS.md:9-42`
- Modify: `README.md:5-38`
- Modify: `docs/roadmap.md:3-16`
- Modify: `docs/decisions/conversation-decisions.md:26-33`
- Verify: all generated artifacts and tests

**Interfaces:**

- Consumes: completed nodes, source, generated bank, and editor.
- Produces: current project instructions and docs that state 139 total nodes, A 27 nodes, 20 assessed nodes, 140 questions, variable quotas, 13 scenario families, and 8 calculation questions.

- [ ] **Step 1: Add a failing stale-fact regression test**

Extend `tests/test_independence.py` or add to `tests/test_project_contract.py`:

```python
def test_current_docs_do_not_claim_retired_a_contract(self):
    current_files = [
        ROOT / "AGENTS.md",
        ROOT / "README.md",
        ROOT / "docs/roadmap.md",
        ROOT / "docs/decisions/conversation-decisions.md",
    ]
    retired = [
        "144 个知识节点", "144 节点知识拼图", "A 板块 192 道", "A 板块 192 题",
        "A 板块 32 个节点", "每个知识节点 6 题", "32 个节点 × 6 题",
    ]
    for path in current_files:
        text = path.read_text(encoding="utf-8")
        for phrase in retired:
            self.assertNotIn(phrase, text, f"{path}: {phrase}")
```

- [ ] **Step 2: Run the stale-fact test and verify red**

Run:

```powershell
python -m unittest tests.test_independence tests.test_project_contract -v
```

Expected: FAIL on the old 144/192/uniform-six facts.

- [ ] **Step 3: Update current project documentation**

Use these exact current facts in all four files:

```text
《碰撞与π》知识拼图共 139 个节点：A=27、B=30、C=46、D=36。
A 板块有 20 个承载题目的二级节点，共 140 道客观题。
题量按知识重要性分配，题库包含 13 个场景题组和 8 道计算题。
```

Keep the existing product boundaries around status questions, answer isolation, and the error-followup Agent.

- [ ] **Step 4: Run deterministic rebuilds twice**

Run this sequence twice:

```powershell
python scripts/build_collision_pi_knowledge_puzzle.py
python scripts/generate_collision_pi_a_questions.py
python scripts/build_collision_pi_question_editor.py
```

Then run:

```powershell
git diff --check
git status --short
```

Expected: the second rebuild produces no new diff beyond the intended implementation changes; no whitespace errors.

- [ ] **Step 5: Run the complete automated suite**

Run:

```powershell
python -m unittest discover -s tests -v
node scripts/validate_question_editor.js
```

Expected: every Python test passes; Node reports 140 questions and 2 script blocks.

- [ ] **Step 6: Run browser acceptance against a UTF-8 server**

Start the author server from the repository root:

```powershell
python -c "import http.server; http.server.SimpleHTTPRequestHandler.extensions_map['.html']='text/html; charset=utf-8'; http.server.ThreadingHTTPServer(('127.0.0.1',8765),http.server.SimpleHTTPRequestHandler).serve_forever()"
```

Open `http://127.0.0.1:8765/authoring/collision-pi-question-editor.html?bank=2` and verify:

- Summary shows 20 assessed knowledge points and 140 questions.
- A3.3 shows 12 questions; A1.3 and A5.2 each show 4.
- Type filtering returns non-zero single-choice, multiple-choice, and multi-blank sets.
- `SC-A3-EQUAL` returns exactly 10 questions.
- `SC-A4-CHASE` returns 15 questions across A4.2 and A5.1 when the node filter is changed accordingly.
- `SC-A7-SPRING` returns 5 questions.
- `standalone` hides every scenario question.
- A nonexistent keyword shows `当前筛选条件下没有题目。`.
- The browser console contains no errors.

- [ ] **Step 7: Review content samples before declaring completion**

Read all 140 prompts once and inspect these exact slices in the editor:

- All 10 questions in `SC-A3-EQUAL` for progressive stages without cross-question dependency.
- All 12 A3.3 questions for unequal-mass coverage and correct signs.
- All 8 calculation questions against their fixtures.
- All 14 A7 questions for explicit stage/system boundaries.
- All 15 A6 questions for the distinction between observed pattern, proof, approximation, and integer boundary.

Reject completion if any prompt contains an unexplained node title, requires a previous answer, hides a needed direction convention, or uses a conservation law outside its stated system and time interval.

- [ ] **Step 8: Commit docs and verification guards**

```powershell
git add AGENTS.md README.md docs/roadmap.md docs/decisions/conversation-decisions.md tests/test_independence.py tests/test_project_contract.py
git commit -m "docs: record the A scenario bank contract"
```

---

## Final Verification Checklist

- [ ] `python -m unittest discover -s tests -v` passes with zero failures.
- [ ] `node scripts/validate_question_editor.js` reports 140 questions.
- [ ] Rebuilding puzzle, bank, and editor twice is idempotent.
- [ ] `git diff --check` is clean.
- [ ] `git status --short` contains only intended implementation files before the final commit and is clean after it.
- [ ] Browser acceptance covers node, type, scenario, standalone, keyword, empty-state, and console checks.
- [ ] All 8 calculation fixtures independently satisfy the stated equations.
- [ ] No current project doc claims 144 total nodes, A 32 nodes, 192 questions, or six questions per node.
