import copy
import json
import math
import os
import re
import subprocess
import unittest
from collections import Counter
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "courses" / "collision-pi" / "question-source-c.json"
SCHEMA = ROOT / "schemas" / "objective_question_source_c.schema.json"
MANIFEST = ROOT / "content" / "courses" / "collision-pi" / "diagram-manifest-c.json"

EXPECTED_QUOTAS = {
    "C1.1": 6, "C1.2": 6, "C1.3": 5, "C1.4": 5,
    "C2.1": 6, "C2.2": 6, "C2.3": 6,
    "C3.1": 6, "C3.2": 6, "C3.3": 7, "C3.4": 4, "C3.5": 3,
    "C4.1": 6, "C4.2": 6, "C4.3": 6, "C4.4": 6,
    "C5.1": 6, "C5.2": 6, "C5.3": 6,
    "C6.1": 6, "C6.2": 6, "C6.3": 6, "C6.4": 6,
    "C7.1": 6, "C7.2": 6, "C7.3": 6, "C7.4": 6,
    "C8.1": 4, "C8.2": 4, "C8.3": 4,
    "C9.1": 1, "C9.2": 1, "C9.3": 2, "C9.4": 2,
    "C9.5": 2, "C9.6": 2, "C9.7": 2,
}

EXPECTED_SCENARIO_NODE_COUNTS = {
    "SC-C1-STATE": {"C1.1": 4, "C1.2": 4, "C1.3": 3, "C1.4": 3},
    "SC-C2-ELLIPSE": {"C2.1": 4, "C2.2": 4, "C2.3": 4},
    "SC-C3-SCALE": {"C3.1": 4, "C3.2": 4, "C3.3": 5, "C3.4": 2, "C3.5": 1},
    "SC-C4-CHORD": {"C4.1": 4, "C4.2": 4, "C4.3": 4, "C4.4": 4},
    "SC-C5-WALL": {"C5.1": 4, "C5.2": 4, "C5.3": 4},
    "SC-C6-CHAIN": {"C6.1": 3, "C6.2": 4, "C6.4": 3},
    "SC-C6-SAFE": {"C6.1": 1, "C6.2": 1, "C6.3": 5, "C6.4": 1},
    "SC-C7-ANGLE": {"C7.1": 3, "C7.2": 3, "C7.3": 2},
    "SC-C7-COUNT": {"C7.1": 1, "C7.2": 1, "C7.3": 2, "C7.4": 4},
    "SC-C8-LEGEND": {"C8.1": 1, "C8.2": 1},
    "SC-C9-WEDGE": {"C9.1": 1},
    "SC-C9-UNFOLD": {"C9.4": 1},
}

EXPECTED_STYLE_BY_STAGE = {
    "C1": {"scenario": 14, "calculation": 2, "concise": 6},
    "C2": {"scenario": 12, "calculation": 3, "concise": 3},
    "C3": {"scenario": 16, "calculation": 5, "concise": 5},
    "C4": {"scenario": 16, "calculation": 4, "concise": 4},
    "C5": {"scenario": 12, "calculation": 2, "concise": 4},
    "C6": {"scenario": 18, "calculation": 3, "concise": 3},
    "C7": {"scenario": 16, "calculation": 4, "concise": 4},
    "C8": {"scenario": 2, "calculation": 0, "concise": 10},
    "C9": {"scenario": 2, "calculation": 1, "concise": 9},
}

EXPECTED_MODE_BY_STAGE = {
    "C1": {"text_only": 8, "stem_figure": 10, "option_figures": 2, "figure_sequence": 2},
    "C2": {"text_only": 6, "stem_figure": 8, "option_figures": 3, "figure_sequence": 1},
    "C3": {"text_only": 9, "stem_figure": 10, "option_figures": 4, "figure_sequence": 3},
    "C4": {"text_only": 6, "stem_figure": 10, "option_figures": 4, "figure_sequence": 4},
    "C5": {"text_only": 6, "stem_figure": 7, "option_figures": 2, "figure_sequence": 3},
    "C6": {"text_only": 7, "stem_figure": 9, "option_figures": 3, "figure_sequence": 5},
    "C7": {"text_only": 6, "stem_figure": 10, "option_figures": 4, "figure_sequence": 4},
    "C8": {"text_only": 5, "stem_figure": 5, "option_figures": 1, "figure_sequence": 1},
    "C9": {"text_only": 7, "stem_figure": 3, "option_figures": 1, "figure_sequence": 1},
}

EXPECTED_SOURCES = {
    "video-main": "sources/theory/弹性碰撞与π.txt",
    "openstax-ellipse": "https://openstax.org/books/precalculus-2e/pages/10-1-the-ellipse",
    "openstax-angles": "https://openstax.org/books/precalculus-2e/pages/5-1-angles",
    "openstax-unit-circle": "https://openstax.org/books/precalculus-2e/pages/5-2-unit-circle-sine-and-cosine-functions",
    "openstax-momentum": "https://openstax.org/books/physics/pages/8-2-conservation-of-momentum",
    "openstax-elastic": "https://openstax.org/books/college-physics/pages/8-4-elastic-collisions-in-one-dimension",
}

EXPECTED_FIXTURE_IDS = (
    "CAL-C1-STATE-01", "CAL-C1-STATE-02",
    "CAL-C2-ELLIPSE-01", "CAL-C2-ELLIPSE-02", "CAL-C2-ELLIPSE-03",
    "CAL-C3-WEIGHT-01", "CAL-C3-WEIGHT-02", "CAL-C3-WEIGHT-03",
    "CAL-C3-CIRCLE-01", "CAL-C3-CIRCLE-02",
    "CAL-C4-LINE-01", "CAL-C4-LINE-02",
    "CAL-C4-INTERSECT-01", "CAL-C4-INTERSECT-02",
    "CAL-C5-WALL-01", "CAL-C5-WALL-02",
    "CAL-C6-CHAIN-01", "CAL-C6-CHAIN-02", "CAL-C6-SAFE-01",
    "CAL-C7-ANGLE-01", "CAL-C7-ANGLE-02",
    "CAL-C7-COUNT-01", "CAL-C7-COUNT-02",
    "CAL-C9-WEDGE-01",
)

EXPECTED_FIXTURE_KINDS = Counter({
    "state_coordinate": 2,
    "ellipse_axes": 3,
    "weighted_transform": 3,
    "energy_circle": 2,
    "momentum_line": 2,
    "line_circle_intersection": 2,
    "wall_reflection": 2,
    "state_chain": 2,
    "terminal_sector": 1,
    "equal_angle": 2,
    "angle_count": 2,
    "wedge_angle": 1,
})

TITLE_TEMPLATES = ("关于“", "判断“", "下列哪项最符合“")
DEPENDENT_REFERENCE = re.compile(
    r"(?:(?:上|前)(?:一)?(?:问|题)|(?:前面|刚才)(?:的)?(?:问|题)|"
    r"(?:继续|沿用|承接)(?:上|前)(?:一)?(?:问|题))"
)
OPTION_POSITION = re.compile(
    r"(?:第[一二三四](?:[、，和及与][一二三四])?项|"
    r"[前后][一二两三四](?:项|组|种状态)|第[一二三四]个选项|第[一二三四]种会|"
    r"(?:最前|最后)(?:一)?(?:项|个选项|种))"
)
IRRELEVANT_OR_META_DISTRACTOR = re.compile(
    r"(?:(?:答案.{0,3}选项|答案.{0,3}排列|选项.{0,3}排列)|颜色|字体|编号|轨道长度|"
    r"(?:物体|小车|滑块).{0,4}命名|(?:质量|动能单位).{0,6}(?:正值|平方)|"
    r"直轨.{0,4}一维|质量都变为零|时间停止)"
)
FORBIDDEN_GRAPH_CONFUSION = (
    "状态点就是物块的位置",
    "换刻度改变了物块速度",
    "动量线就是运动轨迹",
    "圆上的颜色决定碰撞次数",
)
ANGLE_AMBIGUITY = re.compile(r"(?<!2)θ推进|间隔θ(?!与)|圆心角就是θ")


def validate_source_with_pwsh(source):
    env = os.environ.copy()
    env["QUESTION_SOURCE_C_SCHEMA"] = str(SCHEMA)
    script = (
        "$json = [Console]::In.ReadToEnd(); "
        "try { $valid = $json | Test-Json -SchemaFile $env:QUESTION_SOURCE_C_SCHEMA -ErrorAction Stop; "
        "if ($valid) { exit 0 } else { exit 1 } } "
        "catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }"
    )
    return subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", script],
        input=json.dumps(source, ensure_ascii=False),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


class SourceLoadMixin:
    def load_source(self):
        self.assertTrue(SOURCE.is_file(), f"missing C question source: {SOURCE}")
        self.assertTrue(SCHEMA.is_file(), f"missing C question schema: {SCHEMA}")
        self.assertTrue(MANIFEST.is_file(), f"missing C diagram manifest: {MANIFEST}")
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        scenarios = source["scenarios"]
        scenario_questions = [question for scenario in scenarios for question in scenario["questions"]]
        standalone = source["standalone_questions"]
        fixtures = {fixture["id"]: fixture for fixture in source["calculation_fixtures"]}
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        diagram_by_id = {diagram["diagram_id"]: diagram for diagram in manifest["diagrams"]}
        return source, scenarios, scenario_questions, standalone, fixtures, diagram_by_id


class QuestionSourceCSchemaTests(SourceLoadMixin, unittest.TestCase):
    def test_schema_locks_top_level_contract_and_quotas(self):
        self.assertTrue(SCHEMA.is_file(), f"missing C question schema: {SCHEMA}")
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        properties = schema["properties"]
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(properties["course_id"], {"const": "collision-pi"})
        self.assertEqual(properties["section_id"], {"const": "C"})
        self.assertEqual(properties["version"], {"const": "1.0.0"})
        for name, size in (("source_catalog", 6), ("calculation_fixtures", 24),
                           ("scenarios", 12), ("standalone_questions", 72)):
            self.assertEqual(properties[name]["minItems"], size, name)
            self.assertEqual(properties[name]["maxItems"], size, name)
        quotas = properties["node_quotas"]
        self.assertFalse(quotas["additionalProperties"])
        self.assertEqual(set(quotas["required"]), set(EXPECTED_QUOTAS))
        self.assertEqual(
            {node: contract["const"] for node, contract in quotas["properties"].items()},
            EXPECTED_QUOTAS,
        )

    def test_schema_routes_presentation_answer_and_context_payloads(self):
        self.assertTrue(SCHEMA.is_file(), f"missing C question schema: {SCHEMA}")
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        defs = schema["$defs"]
        for definition in ("source", "option", "blank", "question", "scenario"):
            self.assertFalse(defs[definition]["additionalProperties"], definition)
        scenario_rule = defs["scenarioQuestion"]["allOf"][1]
        standalone_rule = defs["standaloneQuestion"]["allOf"][1]
        self.assertIn("ask", scenario_rule["required"])
        self.assertEqual(scenario_rule["not"], {"required": ["prompt"]})
        self.assertIn("prompt", standalone_rule["required"])
        self.assertEqual(standalone_rule["not"], {"required": ["ask"]})
        modes = set(defs["question"]["properties"]["presentation_mode"]["enum"])
        self.assertEqual(modes, {"text_only", "stem_figure", "option_figures", "figure_sequence"})
        scope = set(defs["question"]["properties"]["curriculum_scope"]["enum"])
        self.assertEqual(scope, {"core", "elective"})


class QuestionSourceCTests(SourceLoadMixin, unittest.TestCase):
    def test_exact_source_contract_and_quotas(self):
        source, scenarios, scenario_questions, standalone, _, _ = self.load_source()
        all_questions = scenario_questions + standalone
        self.assertEqual(source["$schema"], "../../../schemas/objective_question_source_c.schema.json")
        self.assertEqual(source["section_id"], "C")
        self.assertEqual(source["node_quotas"], EXPECTED_QUOTAS)
        self.assertEqual(sum(EXPECTED_QUOTAS.values()), 180)
        self.assertEqual(len(scenarios), 12)
        self.assertEqual(len(scenario_questions), 108)
        self.assertEqual(len(standalone), 72)
        self.assertEqual(len(all_questions), 180)
        self.assertEqual(Counter(question["node_id"] for question in all_questions), Counter(EXPECTED_QUOTAS))
        identities = [(question["node_id"], question["key"]) for question in all_questions]
        self.assertEqual(len(identities), len(set(identities)))

    def test_scenario_order_and_exact_node_allocations(self):
        _, scenarios, _, _, _, _ = self.load_source()
        self.assertEqual(tuple(scenario["id"] for scenario in scenarios), tuple(EXPECTED_SCENARIO_NODE_COUNTS))
        for scenario in scenarios:
            self.assertEqual(
                Counter(question["node_id"] for question in scenario["questions"]),
                Counter(EXPECTED_SCENARIO_NODE_COUNTS[scenario["id"]]),
                scenario["id"],
            )

    def test_final_prompts_are_unique(self):
        """Duplicating a question stem must not satisfy a node quota twice."""
        _, _, scenario_questions, standalone, _, _ = self.load_source()
        prompts = [question.get("ask", question.get("prompt")) for question in scenario_questions + standalone]
        self.assertEqual(len(prompts), len(set(prompts)))

    def test_style_type_and_presentation_distributions(self):
        _, _, scenario_questions, standalone, _, _ = self.load_source()
        all_questions = scenario_questions + standalone
        self.assertEqual(
            Counter(question["question_style"] for question in all_questions),
            Counter({"scenario": 108, "calculation": 24, "concise": 48}),
        )
        self.assertEqual(
            Counter(question["presentation_mode"] for question in all_questions),
            Counter({"text_only": 60, "stem_figure": 72, "option_figures": 24, "figure_sequence": 24}),
        )
        self.assertEqual(
            Counter(question["question_type"] for question in all_questions),
            Counter({"single_choice": 108, "multiple_choice": 48, "multi_blank": 24}),
        )
        self.assertTrue(all(question["question_style"] == "scenario" for question in scenario_questions))
        self.assertEqual(Counter(question["question_style"] for question in standalone), Counter({"calculation": 24, "concise": 48}))
        self.assertTrue(all(question["question_type"] == "multi_blank" for question in all_questions if question["question_style"] == "calculation"))
        for stage, expected in EXPECTED_STYLE_BY_STAGE.items():
            selected = [question for question in all_questions if question["node_id"].startswith(f"{stage}.")]
            self.assertEqual(Counter(question["question_style"] for question in selected), Counter(expected), stage)
        for stage, expected in EXPECTED_MODE_BY_STAGE.items():
            selected = [question for question in all_questions if question["node_id"].startswith(f"{stage}.")]
            self.assertEqual(Counter(question["presentation_mode"] for question in selected), Counter(expected), stage)

    def test_source_catalog_scope_and_question_placement(self):
        source, scenarios, scenario_questions, standalone, _, _ = self.load_source()
        self.assertEqual({item["id"]: item["location"] for item in source["source_catalog"]}, EXPECTED_SOURCES)
        for scenario in scenarios:
            self.assertTrue(scenario["context"].strip(), scenario["id"])
            self.assertTrue(scenario["source_refs"], scenario["id"])
            self.assertTrue(set(scenario["source_refs"]).issubset(EXPECTED_SOURCES), scenario["id"])
        for question in scenario_questions:
            self.assertTrue(question["ask"].strip(), question["key"])
            self.assertNotIn("prompt", question, question["key"])
        for question in standalone:
            self.assertTrue(question["prompt"].strip(), question["key"])
            self.assertNotIn("ask", question, question["key"])
        for question in scenario_questions + standalone:
            expected_scope = "elective" if question["node_id"].startswith("C9.") else "core"
            self.assertEqual(question["curriculum_scope"], expected_scope, question["key"])

    def test_image_references_and_option_routing(self):
        _, _, scenario_questions, standalone, _, diagram_by_id = self.load_source()
        all_questions = scenario_questions + standalone
        for question in all_questions:
            mode = question["presentation_mode"]
            options = question.get("options", [])
            if mode == "text_only":
                self.assertNotIn("figure_refs", question, question["key"])
                self.assertTrue(all("figure_ref" not in option for option in options), question["key"])
            elif mode == "stem_figure":
                self.assertEqual(len(question["figure_refs"]), 1, question["key"])
            elif mode == "option_figures":
                self.assertNotIn("figure_refs", question, question["key"])
                self.assertEqual(len(options), 4, question["key"])
                self.assertTrue(all(option.get("figure_ref") in diagram_by_id for option in options), question["key"])
                refs = [option["figure_ref"] for option in options]
                self.assertEqual(len(refs), len(set(refs)), question["key"])
            elif mode == "figure_sequence":
                self.assertGreaterEqual(len(question["figure_refs"]), 2, question["key"])
                self.assertLessEqual(len(question["figure_refs"]), 4, question["key"])
            else:
                self.fail(f"unknown presentation mode: {mode}")
            refs = question.get("figure_refs", []) + [option.get("figure_ref") for option in options if option.get("figure_ref")]
            if refs:
                self.assertTrue(question.get("diagram_focus", "").strip(), question["key"])
                self.assertTrue(all(ref in diagram_by_id for ref in refs), question["key"])
            text = question.get("ask", question.get("prompt", ""))
            if re.search(r"(?<![A-Za-z])[xy](?![A-Za-z])", text):
                coordinates = [diagram_by_id[ref]["coordinate_system"] for ref in refs]
                self.assertTrue(
                    re.search(r"(?:坐标|速度相图|质量加权平面)", text) or coordinates,
                    question["key"],
                )
        for node_id in EXPECTED_QUOTAS:
            if node_id.startswith("C9."):
                continue
            graphical = [question for question in all_questions if question["node_id"] == node_id and question["presentation_mode"] != "text_only"]
            self.assertGreaterEqual(len(graphical), 2, node_id)

    def test_question_payloads_and_wording_guards(self):
        _, _, scenario_questions, standalone, fixtures, _ = self.load_source()
        all_questions = scenario_questions + standalone
        fixture_ids = set(fixtures)
        for question in all_questions:
            self.assertIn(question["difficulty"], {1, 2, 3}, question["key"])
            text = question.get("ask", question.get("prompt", ""))
            self.assertFalse(any(template in text for template in TITLE_TEMPLATES), question["key"])
            self.assertIsNone(DEPENDENT_REFERENCE.search(text), question["key"])
            self.assertIsNone(ANGLE_AMBIGUITY.search(text), question["key"])
            self.assertTrue(question["explanation"].strip(), question["key"])
            self.assertIsNone(OPTION_POSITION.search(question["explanation"]), question["key"])
            for phrase in FORBIDDEN_GRAPH_CONFUSION:
                self.assertNotIn(phrase, text + question["explanation"], question["key"])
            has_options = "options" in question
            has_blanks = "blanks" in question
            self.assertNotEqual(has_options, has_blanks, question["key"])
            if has_options:
                self.assertEqual(len(question["options"]), 4, question["key"])
                self.assertEqual(len({option["text"] for option in question["options"]}), 4, question["key"])
                expected_correct = 1 if question["question_type"] == "single_choice" else 2
                self.assertEqual(sum(option["correct"] for option in question["options"]), expected_correct, question["key"])
                for option in question["options"]:
                    if not option["correct"]:
                        self.assertIsNone(IRRELEVANT_OR_META_DISTRACTOR.search(option["text"]), question["key"])
            else:
                self.assertEqual(question["question_type"], "multi_blank", question["key"])
                self.assertTrue(all(blank["accepted_answers"] for blank in question["blanks"]), question["key"])
            if question["question_style"] == "calculation":
                self.assertIn(question.get("calculation_fixture_id"), fixture_ids, question["key"])
                self.assertEqual(fixtures[question["calculation_fixture_id"]]["node_id"], question["node_id"], question["key"])
            else:
                self.assertNotIn("calculation_fixture_id", question, question["key"])
            if question["node_id"].startswith("C7."):
                self.assertRegex(text, r"(?:弦方向角|圆周角|圆心角|theta|2theta|θ|2θ)", question["key"])

    def test_fixture_ids_kinds_stages_and_physics(self):
        _, _, scenario_questions, standalone, fixtures, _ = self.load_source()
        all_questions = scenario_questions + standalone
        self.assertEqual(tuple(fixtures), EXPECTED_FIXTURE_IDS)
        self.assertEqual(Counter(fixture["kind"] for fixture in fixtures.values()), EXPECTED_FIXTURE_KINDS)
        self.assertEqual(
            Counter(fixture["node_id"].split(".")[0] for fixture in fixtures.values()),
            Counter({"C1": 2, "C2": 3, "C3": 5, "C4": 4, "C5": 2, "C6": 3, "C7": 4, "C9": 1}),
        )
        references = Counter(question["calculation_fixture_id"] for question in all_questions if question["question_style"] == "calculation")
        self.assertEqual(references, Counter(fixtures.keys()))
        for fixture in fixtures.values():
            self.assert_fixture_physics(fixture)

    def test_calculation_answers_are_independently_derived(self):
        _, _, scenario_questions, standalone, fixtures, _ = self.load_source()
        calculations = [question for question in scenario_questions + standalone if question["question_style"] == "calculation"]
        self.assertEqual(len(calculations), 24)
        for question in calculations:
            expected = self.canonical_fixture_answers(fixtures[question["calculation_fixture_id"]])
            for blank in question["blanks"]:
                self.assertIn(blank["id"], expected, question["key"])
                self.assert_answer_contains(blank["accepted_answers"], expected[blank["id"]], question["key"])
        mutation = copy.deepcopy(calculations[0])
        mutation["blanks"][0]["accepted_answers"] = ["999"]
        expected = self.canonical_fixture_answers(fixtures[mutation["calculation_fixture_id"]])
        with self.assertRaises(AssertionError):
            self.assert_answer_contains(mutation["blanks"][0]["accepted_answers"], expected[mutation["blanks"][0]["id"]], mutation["key"])

    def test_c1_c3_checkpoint(self):
        self.assert_checkpoint(("C1.", "C2.", "C3."), 66)

    def test_c4_c6_checkpoint(self):
        self.assert_checkpoint(("C4.", "C5.", "C6."), 66)

    def test_c7_c9_checkpoint(self):
        self.assert_checkpoint(("C7.", "C8.", "C9."), 48)

    def test_schema_accepts_source_and_rejects_context_mutation(self):
        source, _, _, _, _, _ = self.load_source()
        valid = validate_source_with_pwsh(source)
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        mutation = copy.deepcopy(source)
        mutation["scenarios"][0]["questions"][0]["prompt"] = "不允许的独立题字段"
        invalid = validate_source_with_pwsh(mutation)
        self.assertNotEqual(invalid.returncode, 0, invalid.stdout + invalid.stderr)
        mutation = copy.deepcopy(source)
        mutation["standalone_questions"][0]["ask"] = "不允许的场景题字段"
        invalid = validate_source_with_pwsh(mutation)
        self.assertNotEqual(invalid.returncode, 0, invalid.stdout + invalid.stderr)

    def assert_checkpoint(self, prefixes, expected_count):
        _, _, scenario_questions, standalone, fixtures, diagram_by_id = self.load_source()
        questions = [question for question in scenario_questions + standalone if question["node_id"].startswith(prefixes)]
        self.assertEqual(len(questions), expected_count)
        self.assert_question_subset(questions, fixtures, diagram_by_id)
        for question in questions:
            if question["question_style"] == "calculation":
                self.assert_fixture_physics(fixtures[question["calculation_fixture_id"]])

    def assert_question_subset(self, questions, fixtures, diagram_by_id):
        for question in questions:
            self.assertTrue(question.get("ask", question.get("prompt", "")).strip(), question["key"])
            self.assertTrue(question["explanation"].strip(), question["key"])
            self.assertIn(question["presentation_mode"], {"text_only", "stem_figure", "option_figures", "figure_sequence"})
            self.assertIsNone(DEPENDENT_REFERENCE.search(question.get("ask", question.get("prompt", ""))), question["key"])
            refs = question.get("figure_refs", []) + [option.get("figure_ref") for option in question.get("options", []) if option.get("figure_ref")]
            self.assertTrue(all(ref in diagram_by_id for ref in refs), question["key"])
            if question["question_style"] == "calculation":
                self.assertIn(question["calculation_fixture_id"], fixtures, question["key"])
                self.assertEqual(fixtures[question["calculation_fixture_id"]]["node_id"], question["node_id"], question["key"])

    def assert_answer_contains(self, answers, expected, key):
        if isinstance(expected, str):
            self.assertIn(expected, answers, key)
            return
        values = []
        for answer in answers:
            try:
                values.append(float(Fraction(answer.removeprefix("+"))))
            except (ValueError, ZeroDivisionError):
                continue
        self.assertTrue(any(math.isclose(value, expected, rel_tol=1e-8, abs_tol=1e-8) for value in values), f"{key}: expected {expected}")

    def canonical_fixture_answers(self, fixture):
        kind = fixture["kind"]
        if kind == "state_coordinate":
            return {"x": fixture["v_large"], "y": fixture["v_small"]}
        if kind == "ellipse_axes":
            return {
                "a_vM": math.sqrt(2 * fixture["energy"] / fixture["mass_large"]),
                "b_vm": math.sqrt(2 * fixture["energy"] / fixture["mass_small"]),
            }
        if kind == "weighted_transform":
            return {
                "x": math.sqrt(fixture["mass_large"]) * fixture["v_large"],
                "y": math.sqrt(fixture["mass_small"]) * fixture["v_small"],
                "r2": 2 * fixture["energy"],
            }
        if kind == "energy_circle":
            return {"r": math.sqrt(2 * fixture["energy"]), "r2": 2 * fixture["energy"]}
        if kind == "momentum_line":
            return {
                "P": math.sqrt(fixture["mass_large"]) * fixture["x"] + math.sqrt(fixture["mass_small"]) * fixture["y"],
                "slope": -math.sqrt(fixture["mass_large"] / fixture["mass_small"]),
            }
        if kind == "line_circle_intersection":
            return self.line_circle_answers(fixture)
        if kind == "wall_reflection":
            return {"x_after": fixture["x"], "y_after": -fixture["y"]}
        if kind == "state_chain":
            velocities = self.chain_velocities(fixture)
            return {"vM": velocities[0], "vm": velocities[1], "count": len(fixture["events"])}
        if kind == "terminal_sector":
            return {
                "boundary": math.sqrt(fixture["mass_small"] / fixture["mass_large"]) * fixture["x"],
                "safe": "是" if fixture["x"] >= 0 and fixture["y"] >= 0 and fixture["y"] <= math.sqrt(fixture["mass_small"] / fixture["mass_large"]) * fixture["x"] else "否",
            }
        if kind == "equal_angle":
            theta = math.atan(math.sqrt(fixture["mass_small"] / fixture["mass_large"]))
            return {"theta": theta, "step": 2 * theta}
        if kind == "angle_count":
            theta = math.atan(math.sqrt(fixture["mass_small"] / fixture["mass_large"]))
            return {"theta": theta, "step": 2 * theta, "steps": math.floor(fixture["span"] / (2 * theta))}
        if kind == "wedge_angle":
            return {"theta": math.atan(math.sqrt(fixture["mass_small"] / fixture["mass_large"]))}
        self.fail(f"unknown fixture kind: {kind}")

    def assert_fixture_physics(self, fixture):
        answers = self.canonical_fixture_answers(fixture)
        for key, value in answers.items():
            actual = fixture["expected"][key]
            if isinstance(value, str):
                self.assertEqual(actual, value, fixture["id"])
            else:
                self.assertAlmostEqual(actual, value, places=8, msg=fixture["id"])
        if fixture["kind"] == "line_circle_intersection":
            roots = fixture["expected"]["roots"]
            self.assertEqual(len(roots), 2, fixture["id"])
            for root in roots:
                self.assertAlmostEqual(root["x"] ** 2 + root["y"] ** 2, 2 * fixture["energy"], places=8)
                self.assertAlmostEqual(math.sqrt(fixture["mass_large"]) * root["x"] + math.sqrt(fixture["mass_small"]) * root["y"], fixture["momentum"], places=8)
        if fixture["kind"] == "state_chain":
            self.chain_velocities(fixture, assert_events=True)
        if fixture["kind"] == "terminal_sector":
            slope = math.sqrt(fixture["mass_small"] / fixture["mass_large"])
            self.assertGreaterEqual(fixture["x"], 0)
            self.assertGreaterEqual(fixture["y"], 0)
            self.assertLessEqual(fixture["y"], slope * fixture["x"])

    def line_circle_answers(self, fixture):
        mass_large, mass_small = fixture["mass_large"], fixture["mass_small"]
        coefficient = math.sqrt(mass_large / mass_small)
        constant = fixture["momentum"] / math.sqrt(mass_small)
        radius_squared = 2 * fixture["energy"]
        a = 1 + coefficient ** 2
        b = -2 * coefficient * constant
        c = constant ** 2 - radius_squared
        discriminant = b ** 2 - 4 * a * c
        xs = sorted(((-b - math.sqrt(discriminant)) / (2 * a), (-b + math.sqrt(discriminant)) / (2 * a)))
        roots = [{"x": x, "y": constant - coefficient * x} for x in xs]
        return {"x1": roots[0]["x"], "y1": roots[0]["y"], "x2": roots[1]["x"], "y2": roots[1]["y"]}

    def chain_velocities(self, fixture, assert_events=False):
        velocities = list(fixture["initial_velocities"])
        mass_large, mass_small = fixture["mass_large"], fixture["mass_small"]
        for event in fixture["events"]:
            if event["kind"] == "block_collision":
                large, small = velocities
                velocities = [
                    ((mass_large - mass_small) * large + 2 * mass_small * small) / (mass_large + mass_small),
                    (2 * mass_large * large + (mass_small - mass_large) * small) / (mass_large + mass_small),
                ]
            elif event["kind"] == "wall_reflection":
                velocities[1] = -velocities[1]
            else:
                self.fail(f"unknown state-chain event: {event['kind']}")
            if assert_events:
                self.assertEqual(len(event["expected_velocities"]), 2, fixture["id"])
                for actual, expected in zip(velocities, event["expected_velocities"]):
                    self.assertAlmostEqual(actual, expected, places=8, msg=fixture["id"])
        return velocities


if __name__ == "__main__":
    unittest.main()
