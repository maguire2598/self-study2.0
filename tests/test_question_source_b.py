import copy
import difflib
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
SOURCE = ROOT / "content/courses/collision-pi/question-source-b.json"
SCHEMA = ROOT / "schemas/objective_question_source_b.schema.json"

EXPECTED_QUOTAS = {
    "B1.1": 6, "B1.2": 6, "B1.3": 6, "B1.4": 6,
    "B2.1": 8, "B2.2": 10, "B2.3": 8, "B2.4": 6,
    "B3.1": 6, "B3.2": 8, "B3.3": 8, "B3.4": 10, "B3.5": 6,
    "B4.1": 10, "B4.2": 12, "B4.3": 10, "B4.4": 8, "B4.5": 6,
    "B5.1": 8, "B5.2": 8, "B5.3": 8, "B5.4": 4,
}

EXPECTED_SCENARIO_NODE_COUNTS = {
    "SC-B1-RECORD": {"B1.1": 4, "B1.4": 4},
    "SC-B1-IMPULSE": {"B1.2": 4},
    "SC-B1-ENERGY": {"B1.3": 4},
    "SC-B2-BOUNDARY": {"B2.1": 6, "B2.4": 4},
    "SC-B2-CONSERVE": {"B2.2": 8},
    "SC-B2-ELASTICITY": {"B2.3": 6},
    "SC-B3-EQUATIONS": {"B3.1": 4, "B3.2": 6, "B3.3": 6},
    "SC-B3-RELATIVE": {"B3.4": 8},
    "SC-B3-RESTITUTION": {"B3.5": 4},
    "SC-B4-SOLVE": {"B4.1": 9, "B4.2": 11},
    "SC-B4-RATIO": {"B4.3": 9},
    "SC-B4-CHECK": {"B4.4": 7, "B4.5": 5},
    "SC-B5-CHAIN": {"B5.1": 8, "B5.2": 8},
    "SC-B5-TERMINAL": {"B5.3": 8},
    "SC-B5-GEOMETRY": {"B5.4": 3},
}

EXPECTED_SCENARIO_IDS = tuple(EXPECTED_SCENARIO_NODE_COUNTS)
EXPECTED_SOURCES = {
    "video-main": "sources/theory/弹性碰撞与π.txt",
    "openstax-momentum": "https://openstax.org/books/college-physics/pages/8-1-linear-momentum-and-force",
    "openstax-impulse": "https://openstax.org/books/college-physics/pages/8-2-impulse",
    "openstax-conservation": "https://openstax.org/books/college-physics/pages/8-3-conservation-of-momentum",
    "openstax-elastic": "https://openstax.org/books/college-physics/pages/8-4-elastic-collisions-in-one-dimension",
}
EXPECTED_FIXTURE_KINDS = Counter({
    "momentum_impulse": 4,
    "energy_audit": 4,
    "elastic_1d": 16,
    "restitution_1d": 4,
    "collision_chain": 4,
})
EXPECTED_STANDALONE_NODE_COUNTS = {
    **{f"B1.{index}": 2 for index in range(1, 5)},
    **{f"B2.{index}": 2 for index in range(1, 5)},
    **{f"B3.{index}": 2 for index in range(1, 6)},
    **{f"B4.{index}": 1 for index in range(1, 6)},
    "B5.4": 1,
}

TITLE_TEMPLATES = ("关于“", "判断“", "下列哪项最符合“")
DEPENDENT_REFERENCE = re.compile(
    r"(?:(?:上|前)(?:一)?(?:问|题)|(?:前面|刚才)(?:的)?(?:问|题)|"
    r"(?:继续|沿用|承接)(?:上|前)(?:一)?(?:问|题))"
)
OPTION_POSITION = re.compile(
    r"(?:第[一二三四](?:[、，和及与][一二三四])?项|"
    r"[前后][一二两三四](?:项|组|种状态)|第[一二三四]个选项|第[一二三四]种会)"
)
IRRELEVANT_OR_META_DISTRACTOR = re.compile(
    r"(?:(?:答案.{0,3}选项|答案.{0,3}排列|选项.{0,3}排列)|颜色|字体|编号|轨道长度|"
    r"(?:物体|小车|滑块).{0,4}命名|"
    r"(?:质量|动能单位).{0,6}(?:正值|平方)|直轨.{0,4}一维|质量都变为零|时间停止)"
)
POSITIVE_DIRECTION = re.compile(r"(?:规定|取|以)向[左右]为正")
SYSTEM_SELECTION = re.compile(r"(?:以|选取|选择).{0,24}(?:为|组成的)(?:研究)?系统")
RESEARCH_INTERVAL = re.compile(
    r"(?:碰撞开始至碰撞结束|碰撞的短暂时间内|碰撞过程中|作用时间内|研究时段内|"
    r"从[^，。；]{1,24}到[^，。；]{1,24}(?:的)?(?:阶段|过程|时段|时间内))"
)
NEGLIGIBLE_EXTERNAL_IMPULSE = re.compile(
    r"(?:水平)?(?:系统)?外冲量.{0,8}(?:可忽略|为零|近似为零)"
)
MAX_GROUPED_CONCISE_SIMILARITY = 0.53


def semantic_question_text(question):
    correct_payload = "".join(
        option["text"] for option in question.get("options", []) if option["correct"]
    ) + "".join(blank["accepted_answers"][0] for blank in question.get("blanks", []))
    text = question.get("ask", question.get("prompt", "")) + question["explanation"] + correct_payload
    return re.sub(r"[，。；：、？（）()_+\-×=·/\s\dA-Za-z]+", "", text)


def validate_source_with_pwsh(source):
    env = os.environ.copy()
    env["QUESTION_SOURCE_B_SCHEMA"] = str(SCHEMA)
    script = (
        "$json = [Console]::In.ReadToEnd(); "
        "try { "
        "$valid = $json | Test-Json -SchemaFile $env:QUESTION_SOURCE_B_SCHEMA -ErrorAction Stop; "
        "if ($valid) { exit 0 } else { exit 1 } "
        "} catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }"
    )
    return subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", script],
        input=json.dumps(source, ensure_ascii=False),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


class QuestionSourceBSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        cls.defs = cls.schema["$defs"]

    def test_schema_locks_top_level_identity_and_exact_collection_sizes(self):
        properties = self.schema["properties"]
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(self.schema["additionalProperties"])
        self.assertEqual(properties["course_id"], {"const": "collision-pi"})
        self.assertEqual(properties["section_id"], {"const": "B"})
        self.assertEqual(properties["version"], {"const": "1.0.0"})
        for name, size in (("source_catalog", 5), ("calculation_fixtures", 32),
                           ("scenarios", 15), ("standalone_questions", 32)):
            self.assertEqual(properties[name]["minItems"], size, name)
            self.assertEqual(properties[name]["maxItems"], size, name)

    def test_schema_locks_all_quota_names_and_values(self):
        quotas = self.schema["properties"]["node_quotas"]
        self.assertFalse(quotas["additionalProperties"])
        self.assertEqual(set(quotas["required"]), set(EXPECTED_QUOTAS))
        self.assertEqual(set(quotas["properties"]), set(EXPECTED_QUOTAS))
        for node_id, quota in EXPECTED_QUOTAS.items():
            self.assertEqual(quotas["properties"][node_id], {"const": quota})

    def test_schema_pins_source_and_scenario_ids_in_order(self):
        cases = (
            ("source_catalog", tuple(EXPECTED_SOURCES), "#/$defs/source"),
            ("scenarios", EXPECTED_SCENARIO_IDS, "#/$defs/scenario"),
        )
        for property_name, expected_ids, definition_ref in cases:
            collection = self.schema["properties"][property_name]
            self.assertIs(collection["items"], False, property_name)
            self.assertEqual(len(collection["prefixItems"]), len(expected_ids))
            actual_ids = []
            for item in collection["prefixItems"]:
                self.assertEqual(item["allOf"][0], {"$ref": definition_ref})
                actual_ids.append(item["allOf"][1]["properties"]["id"]["const"])
            self.assertEqual(tuple(actual_ids), expected_ids)

    def test_schema_defines_closed_fixture_branches(self):
        expected = {
            "momentumImpulseFixture", "energyAuditFixture", "elasticFixture",
            "restitutionFixture", "collisionChainFixture",
        }
        actual_refs = {
            branch["$ref"].removeprefix("#/$defs/")
            for branch in self.defs["calculationFixture"]["oneOf"]
        }
        self.assertEqual(actual_refs, expected)
        for definition in expected | {"source", "option", "blank", "question", "scenario"}:
            self.assertFalse(self.defs[definition]["additionalProperties"], definition)

    def test_schema_routes_text_answer_and_calculation_payloads(self):
        scenario_question = self.defs["scenarioQuestion"]
        standalone_question = self.defs["standaloneQuestion"]
        self.assertIn("ask", scenario_question["required"])
        self.assertEqual(scenario_question["not"], {"required": ["prompt"]})
        self.assertIn("prompt", standalone_question["required"])
        self.assertEqual(standalone_question["not"], {"required": ["ask"]})
        self.assertEqual(
            self.defs["scenario"]["properties"]["questions"]["items"],
            {"$ref": "#/$defs/scenarioQuestion"},
        )
        self.assertEqual(
            self.schema["properties"]["standalone_questions"]["items"],
            {"$ref": "#/$defs/standaloneQuestion"},
        )

        type_branches = {
            branch["if"]["properties"]["question_type"]["const"]: branch["then"]
            for branch in self.defs["question"]["allOf"]
            if "question_type" in branch.get("if", {}).get("properties", {})
        }
        for question_type in ("single_choice", "multiple_choice"):
            self.assertIn("options", type_branches[question_type]["required"])
            self.assertEqual(type_branches[question_type]["not"], {"required": ["blanks"]})
        self.assertIn("blanks", type_branches["multi_blank"]["required"])
        self.assertEqual(type_branches["multi_blank"]["not"], {"required": ["options"]})
        calculation_branch = next(
            branch for branch in self.defs["question"]["allOf"]
            if branch.get("if", {}).get("properties", {}).get("question_style", {}).get("const")
            == "calculation"
        )
        self.assertIn("calculation_fixture_id", calculation_branch["then"]["required"])

    def test_schema_extends_variant_axes_without_losing_a_axes(self):
        axes = set(self.defs["question"]["properties"]["variant_axis"]["enum"])
        accepted_a = {
            "mass_ratio", "initial_velocity", "friction", "elasticity", "incline",
            "spring", "system_boundary", "counting", "direction", "observation",
            "model_assumption", "event_sequence",
        }
        added_b = {
            "impulse", "energy", "conservation", "equation_setup",
            "solution_method", "restitution", "limit", "state_geometry",
        }
        self.assertTrue(accepted_a | added_b <= axes)


class QuestionSourceBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.scenario_questions = [
            question
            for scenario in cls.source["scenarios"]
            for question in scenario["questions"]
        ]
        cls.standalone = cls.source["standalone_questions"]
        cls.all_questions = cls.scenario_questions + cls.standalone
        cls.fixtures = {fixture["id"]: fixture for fixture in cls.source["calculation_fixtures"]}

    def test_exact_source_contract_and_quotas(self):
        source = self.source
        scenario_questions = self.scenario_questions
        all_questions = self.all_questions
        self.assertEqual(source["section_id"], "B")
        self.assertEqual(source["node_quotas"], EXPECTED_QUOTAS)
        self.assertEqual(sum(EXPECTED_QUOTAS.values()), 168)
        self.assertEqual(len(source["scenarios"]), 15)
        self.assertEqual(len(scenario_questions), 136)
        self.assertEqual(len(source["standalone_questions"]), 32)
        self.assertEqual(
            Counter(q["question_style"] for q in all_questions),
            Counter({"scenario": 104, "calculation": 32, "concise": 32}),
        )
        self.assertEqual(
            Counter(question["node_id"] for question in all_questions),
            Counter(EXPECTED_QUOTAS),
        )

    def test_scenario_order_and_exact_node_allocations(self):
        self.assertEqual(
            tuple(scenario["id"] for scenario in self.source["scenarios"]),
            tuple(EXPECTED_SCENARIO_NODE_COUNTS),
        )
        for scenario in self.source["scenarios"]:
            actual = Counter(question["node_id"] for question in scenario["questions"])
            self.assertEqual(actual, Counter(EXPECTED_SCENARIO_NODE_COUNTS[scenario["id"]]), scenario["id"])

    def test_exact_standalone_distribution(self):
        self.assertEqual(
            Counter(question["node_id"] for question in self.standalone),
            Counter(EXPECTED_STANDALONE_NODE_COUNTS),
        )

    def test_question_keys_difficulty_types_and_payloads(self):
        identities = [(question["node_id"], question["key"]) for question in self.all_questions]
        self.assertEqual(len(identities), len(set(identities)))
        type_counts = Counter(question["question_type"] for question in self.all_questions)
        self.assertTrue(all(type_counts[kind] for kind in ("single_choice", "multiple_choice", "multi_blank")))
        self.assertGreaterEqual(type_counts["multi_blank"], 32)
        fixture_ids = set(self.fixtures)
        for question in self.all_questions:
            self.assertIn(question["difficulty"], {1, 2, 3}, question["key"])
            has_options = "options" in question
            has_blanks = "blanks" in question
            self.assertNotEqual(has_options, has_blanks, question["key"])
            if question["question_type"] in {"single_choice", "multiple_choice"}:
                self.assertTrue(has_options, question["key"])
                self.assertEqual(len(question["options"]), 4, question["key"])
                option_texts = [option["text"] for option in question["options"]]
                self.assertEqual(len(option_texts), len(set(option_texts)), question["key"])
                correct = sum(option["correct"] for option in question["options"])
                expected = 1 if question["question_type"] == "single_choice" else 2
                self.assertEqual(correct, expected, question["key"])
            else:
                self.assertTrue(has_blanks, question["key"])
                blank_ids = [blank["id"] for blank in question["blanks"]]
                self.assertEqual(len(blank_ids), len(set(blank_ids)), question["key"])
                self.assertTrue(all(blank["accepted_answers"] for blank in question["blanks"]), question["key"])
            if question["question_style"] == "calculation":
                self.assertIn(question.get("calculation_fixture_id"), fixture_ids, question["key"])
                self.assertEqual(
                    self.fixtures[question["calculation_fixture_id"]]["node_id"],
                    question["node_id"],
                    question["key"],
                )
            else:
                self.assertNotIn("calculation_fixture_id", question, question["key"])

    def test_grouped_and_standalone_placement(self):
        self.assertTrue(all(q["question_style"] in {"scenario", "calculation"} for q in self.scenario_questions))
        self.assertTrue(all(q["question_style"] == "concise" for q in self.standalone))
        for question in self.scenario_questions:
            self.assertTrue(question["ask"].strip(), question["key"])
            self.assertNotIn("prompt", question, question["key"])
        for question in self.standalone:
            self.assertTrue(question["prompt"].strip(), question["key"])
            self.assertNotIn("ask", question, question["key"])

    def test_source_catalog_and_references_are_complete(self):
        actual = {item["id"]: item["location"] for item in self.source["source_catalog"]}
        self.assertEqual(actual, EXPECTED_SOURCES)
        self.assertEqual(len(self.source["source_catalog"]), 5)
        for scenario in self.source["scenarios"]:
            self.assertTrue(scenario["context"].strip(), scenario["id"])
            self.assertTrue(set(scenario["source_refs"]).issubset(EXPECTED_SOURCES), scenario["id"])

    def test_draft202012_schema_accepts_source_and_rejects_payload_mutations(self):
        valid = validate_source_with_pwsh(self.source)
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        mutations = []
        grouped_prompt = copy.deepcopy(self.source)
        grouped_prompt["scenarios"][0]["questions"][0]["prompt"] = "不允许的字段"
        mutations.append(("grouped prompt", grouped_prompt))
        concise_ask = copy.deepcopy(self.source)
        concise_ask["standalone_questions"][0]["ask"] = "不允许的字段"
        mutations.append(("concise ask", concise_ask))
        choice_blanks = copy.deepcopy(self.source)
        choice_blanks["scenarios"][0]["questions"][1]["blanks"] = [
            {"id": "x", "accepted_answers": ["x"]}
        ]
        mutations.append(("choice blanks", choice_blanks))
        for label, mutation in mutations:
            with self.subTest(label=label):
                result = validate_source_with_pwsh(mutation)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_wording_guards_and_shuffle_safe_explanations(self):
        self.assertIsNone(DEPENDENT_REFERENCE.search("第一次碰撞后、第二次碰撞前"))
        for question in self.all_questions:
            text = question.get("ask", question.get("prompt", ""))
            self.assertFalse(any(template in text for template in TITLE_TEMPLATES), question["key"])
            self.assertIsNone(DEPENDENT_REFERENCE.search(text), question["key"])
            self.assertIsNone(OPTION_POSITION.search(question["explanation"]), question["key"])
            for option in question.get("options", []):
                if option["correct"]:
                    continue
                self.assertIsNone(
                    IRRELEVANT_OR_META_DISTRACTOR.search(option["text"]),
                    question["key"],
                )

    def test_grouped_and_concise_questions_are_not_rephrased_duplicates(self):
        for grouped in self.scenario_questions:
            grouped_text = semantic_question_text(grouped)
            for concise in self.standalone:
                if concise["node_id"] != grouped["node_id"]:
                    continue
                similarity = difflib.SequenceMatcher(
                    None, grouped_text, semantic_question_text(concise)
                ).ratio()
                self.assertLess(
                    similarity,
                    MAX_GROUPED_CONCISE_SIMILARITY,
                    f"{grouped['key']} / {concise['key']} = {similarity:.3f}",
                )

    def test_direction_and_conservation_prompts_state_needed_conditions(self):
        scenario_context = {scenario["id"]: scenario["context"] for scenario in self.source["scenarios"]}
        for scenario in self.source["scenarios"]:
            for question in scenario["questions"]:
                text = f"{scenario_context[scenario['id']]} {question['ask']}"
                if question["variant_axis"] == "direction":
                    self.assertRegex(text, POSITIVE_DIRECTION, question["key"])
                if question["variant_axis"] == "conservation":
                    self.assertRegex(text, SYSTEM_SELECTION, question["key"])
                    self.assertRegex(text, RESEARCH_INTERVAL, question["key"])
                if question["question_style"] == "calculation":
                    fixture = self.fixtures[question["calculation_fixture_id"]]
                    if fixture["kind"] in {"elastic_1d", "restitution_1d"}:
                        self.assertRegex(text, SYSTEM_SELECTION, question["key"])
                        self.assertRegex(text, RESEARCH_INTERVAL, question["key"])
                        self.assertRegex(text, NEGLIGIBLE_EXTERNAL_IMPULSE, question["key"])
        for question in self.standalone:
            text = question["prompt"]
            if question["variant_axis"] == "direction":
                self.assertRegex(text, POSITIVE_DIRECTION, question["key"])
            if question["variant_axis"] == "conservation":
                self.assertRegex(text, SYSTEM_SELECTION, question["key"])
                self.assertRegex(text, RESEARCH_INTERVAL, question["key"])

    def test_energy_conservation_with_sound_uses_an_energy_closed_system(self):
        question = next(q for q in self.all_questions if q["key"] == "b2-3-elasticity-04")
        text = question["ask"]
        self.assertRegex(text, r"(?:选取|选择).{0,40}环境.{0,24}系统")
        self.assertRegex(text, r"(?:系统外|更外界).{0,12}能量传递.{0,8}可忽略")

    def test_b2_4_includes_a_movable_wall_system_boundary(self):
        questions = [q for q in self.all_questions if q["node_id"] == "B2.4"]
        movable_wall_questions = [
            question
            for question in questions
            if "可移动" in question.get("ask", question.get("prompt", ""))
        ]
        self.assertTrue(movable_wall_questions)
        text = " ".join(
            question.get("ask", question.get("prompt", ""))
            + " "
            + question["explanation"]
            + " "
            + " ".join(option["text"] for option in question.get("options", []))
            for question in movable_wall_questions
        )
        self.assertIn("反冲", text)
        self.assertIn("系统", text)

    def test_fixture_kind_counts_references_and_physics(self):
        fixtures = list(self.fixtures.values())
        self.assertEqual(len(fixtures), 32)
        self.assertEqual(Counter(fixture["kind"] for fixture in fixtures), EXPECTED_FIXTURE_KINDS)
        references = Counter(
            question["calculation_fixture_id"]
            for question in self.all_questions
            if question["question_style"] == "calculation"
        )
        self.assertEqual(references, Counter(self.fixtures.keys()))
        for fixture in fixtures:
            self.assert_fixture_physics(fixture)

    def test_every_calculation_accepts_answers_derived_from_its_fixture(self):
        calculation_questions = [
            question
            for question in self.all_questions
            if question["question_style"] == "calculation"
        ]
        self.assertEqual(len(calculation_questions), 32)
        for question in calculation_questions:
            self.assert_question_accepts_fixture_answers(question)

        mutation = copy.deepcopy(
            next(q for q in calculation_questions if q["key"] == "b4-2-solve-04")
        )
        mutation["blanks"][0]["accepted_answers"] = ["8/3"]
        with self.assertRaises(AssertionError):
            self.assert_question_accepts_fixture_answers(mutation)

    def assert_question_accepts_fixture_answers(self, question):
        fixture = self.fixtures[question["calculation_fixture_id"]]
        canonical = self.canonical_fixture_answers(fixture)
        for blank in question["blanks"]:
            self.assertIn(blank["id"], canonical, question["key"])
            expected = canonical[blank["id"]]
            if isinstance(expected, str):
                self.assertIn(expected, blank["accepted_answers"], question["key"])
                continue
            numeric_answers = []
            for answer in blank["accepted_answers"]:
                try:
                    numeric_answers.append(float(Fraction(answer.removeprefix("+"))))
                except (ValueError, ZeroDivisionError):
                    continue
            self.assertTrue(
                any(math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9)
                    for actual in numeric_answers),
                f"{question['key']}:{blank['id']} expected {expected}",
            )

    def canonical_fixture_answers(self, fixture):
        kind = fixture["kind"]
        if kind == "momentum_impulse":
            p0 = fixture["mass"] * fixture["u"]
            p1 = fixture["mass"] * fixture["v"]
            return {"p0": p0, "p1": p1, "dp": p1 - p0, "i": p1 - p0}
        if kind == "energy_audit":
            k0 = sum(0.5 * m * u ** 2 for m, u in zip(fixture["masses"], fixture["before"]))
            k1 = sum(0.5 * m * v ** 2 for m, v in zip(fixture["masses"], fixture["after"]))
            return {"k0": k0, "k1": k1, "dk": k1 - k0}
        if kind in {"elastic_1d", "restitution_1d"}:
            m1, m2 = fixture["m1"], fixture["m2"]
            u1, u2 = fixture["u1"], fixture["u2"]
            e = 1 if kind == "elastic_1d" else fixture["e"]
            v1 = (m1 * u1 + m2 * u2 - m2 * e * (u1 - u2)) / (m1 + m2)
            v2 = (m1 * u1 + m2 * u2 + m1 * e * (u1 - u2)) / (m1 + m2)
            momentum = m1 * u1 + m2 * u2
            return {
                "v1": v1,
                "v2": v2,
                "relative": v2 - v1,
                "p0": momentum,
                "p1": m1 * v1 + m2 * v2,
            }
        if kind == "collision_chain":
            velocities = list(fixture["initial"]["velocities"])
            for event in fixture["events"]:
                if event["type"] == "object_collision":
                    m1, m2 = fixture["masses"]
                    u1, u2 = velocities
                    velocities = [
                        ((m1 - m2) * u1 + 2 * m2 * u2) / (m1 + m2),
                        (2 * m1 * u1 + (m2 - m1) * u2) / (m1 + m2),
                    ]
                else:
                    velocities[event["object"]] = -velocities[event["object"]]
            if velocities[1] < 0:
                next_wall = 1 + sum(event["type"] == "fixed_wall" for event in fixture["events"])
                next_event = f"小滑块第{'一二三四五'[next_wall - 1]}次撞墙"
            elif fixture["terminal"]["expected"]["has_future_contact"]:
                next_objects = 1 + sum(
                    event["type"] == "object_collision" for event in fixture["events"]
                )
                next_event = f"第{'一二三四五'[next_objects - 1]}次物块碰撞"
            else:
                next_event = "终止"
            return {
                "vM": velocities[0],
                "vm": velocities[1],
                "next": next_event,
                "count": len(fixture["events"]),
            }
        self.fail(f"unknown calculation kind: {kind}")

    def assert_fixture_physics(self, fixture):
        kind = fixture["kind"]
        if kind == "momentum_impulse":
            p0 = fixture["mass"] * fixture["u"]
            p1 = fixture["mass"] * fixture["v"]
            self.assertAlmostEqual(fixture["expected"]["p_before"], p0)
            self.assertAlmostEqual(fixture["expected"]["p_after"], p1)
            self.assertAlmostEqual(fixture["expected"]["delta_p"], p1 - p0)
            self.assertAlmostEqual(fixture["expected"]["impulse"], p1 - p0)
        elif kind == "energy_audit":
            before = sum(0.5 * m * u ** 2 for m, u in zip(fixture["masses"], fixture["before"]))
            after = sum(0.5 * m * v ** 2 for m, v in zip(fixture["masses"], fixture["after"]))
            self.assertAlmostEqual(fixture["expected"]["k_before"], before)
            self.assertAlmostEqual(fixture["expected"]["k_after"], after)
            self.assertAlmostEqual(fixture["expected"]["delta_k"], after - before)
        elif kind in {"elastic_1d", "restitution_1d"}:
            m1, m2 = fixture["m1"], fixture["m2"]
            u1, u2 = fixture["u1"], fixture["u2"]
            e = 1 if kind == "elastic_1d" else fixture["e"]
            v1 = (m1 * u1 + m2 * u2 - m2 * e * (u1 - u2)) / (m1 + m2)
            v2 = (m1 * u1 + m2 * u2 + m1 * e * (u1 - u2)) / (m1 + m2)
            self.assertAlmostEqual(fixture["expected"]["v1"], v1)
            self.assertAlmostEqual(fixture["expected"]["v2"], v2)
            self.assertAlmostEqual(m1 * u1 + m2 * u2, m1 * v1 + m2 * v2)
            self.assertAlmostEqual(v2 - v1, e * (u1 - u2))
        elif kind == "collision_chain":
            self.assert_chain_states_match_event_updates(fixture)
        else:
            self.fail(f"unknown calculation kind: {kind}")

    def assert_chain_states_match_event_updates(self, fixture):
        velocities = list(fixture["initial"]["velocities"])
        masses = fixture["masses"]
        for event in fixture["events"]:
            if event["type"] == "object_collision":
                m1, m2 = masses
                u1, u2 = velocities
                velocities = [
                    ((m1 - m2) * u1 + 2 * m2 * u2) / (m1 + m2),
                    (2 * m1 * u1 + (m2 - m1) * u2) / (m1 + m2),
                ]
            elif event["type"] == "fixed_wall":
                velocities[event["object"]] = -velocities[event["object"]]
            else:
                self.fail(f"unknown chain event: {event['type']}")
            self.assertEqual(len(event["expected_velocities"]), 2)
            for actual, expected in zip(velocities, event["expected_velocities"]):
                self.assertAlmostEqual(actual, expected)

        terminal = fixture["terminal"]
        positions = terminal["positions"]
        left = terminal["left_object"]
        right = terminal["right_object"]
        self.assertLess(positions[left], positions[right])
        gap = positions[right] - positions[left]
        closing_speed = velocities[left] - velocities[right]
        has_future_contact = gap > 0 and closing_speed > 0
        self.assertAlmostEqual(terminal["expected"]["gap"], gap)
        self.assertAlmostEqual(terminal["expected"]["closing_speed"], closing_speed)
        self.assertEqual(terminal["expected"]["has_future_contact"], has_future_contact)
        self.assertEqual(terminal["expected"]["collision_count"], len(fixture["events"]))

    def test_chain_fixtures_derive_every_event_and_collision_count(self):
        chain_fixtures = [
            fixture for fixture in self.fixtures.values()
            if fixture["kind"] == "collision_chain"
        ]
        self.assertEqual(len(chain_fixtures), 4)
        for fixture in chain_fixtures:
            self.assert_chain_states_match_event_updates(fixture)

    def test_b1_b2_checkpoint_content(self):
        selected = [
            scenario for scenario in self.source["scenarios"]
            if scenario["id"].startswith(("SC-B1-", "SC-B2-"))
        ]
        self.assertEqual(len(selected), 6)
        questions = [question for scenario in selected for question in scenario["questions"]]
        self.assertEqual(len(questions), 40)
        self.assertEqual(sum(q["question_style"] == "calculation" for q in questions), 8)
        self.assert_checkpoint_questions(selected)
        for question in questions:
            if question["question_style"] == "calculation":
                self.assert_fixture_physics(self.fixtures[question["calculation_fixture_id"]])

    def test_b3_checkpoint_content(self):
        selected = [scenario for scenario in self.source["scenarios"] if scenario["id"].startswith("SC-B3-")]
        questions = [question for scenario in selected for question in scenario["questions"]]
        self.assertEqual(len(questions), 28)
        self.assertEqual(sum(q["question_style"] == "calculation" for q in questions), 8)
        joined = " ".join(q["ask"] for q in questions)
        for phrase in ("静止", "相向", "同向追赶", "不会相碰"):
            self.assertIn(phrase, joined)
        for phrase in ("e=1", "0<e<1", "e=0"):
            self.assertIn(phrase, joined)
        self.assert_checkpoint_questions(selected)
        self.assert_checkpoint_fixture_physics(questions)

    def test_b4_checkpoint_content(self):
        selected = [scenario for scenario in self.source["scenarios"] if scenario["id"].startswith("SC-B4-")]
        questions = [question for scenario in selected for question in scenario["questions"]]
        self.assertEqual(len(questions), 41)
        self.assertEqual(sum(q["question_style"] == "calculation" for q in questions), 12)
        joined = " ".join(q["ask"] for q in questions)
        for phrase in ("消元", "平方差", "通式", "等质量", "1:3", "3:1", "质量远大于"):
            self.assertIn(phrase, joined)
        for phrase in ("动量", "动能", "相对速度", "量纲", "平凡解"):
            self.assertIn(phrase, joined)
        self.assert_checkpoint_questions(selected)
        self.assert_checkpoint_fixture_physics(questions)

    def test_b5_checkpoint_content(self):
        selected = [scenario for scenario in self.source["scenarios"] if scenario["id"].startswith("SC-B5-")]
        questions = [question for scenario in selected for question in scenario["questions"]]
        self.assertEqual(len(questions), 27)
        self.assertEqual(sum(q["question_style"] == "calculation" for q in questions), 4)
        joined = " ".join(q["ask"] for q in questions)
        for phrase in ("第一次碰撞", "墙", "第二次物块碰撞", "下一事件", "终止", "碰撞次数", "大物块停下"):
            self.assertIn(phrase, joined)
        self.assert_checkpoint_questions(selected)
        self.assert_checkpoint_fixture_physics(questions)

    def assert_checkpoint_fixture_physics(self, questions):
        for question in questions:
            if question["question_style"] == "calculation":
                self.assert_fixture_physics(self.fixtures[question["calculation_fixture_id"]])

    def assert_checkpoint_questions(self, scenarios):
        fixture_ids = set(self.fixtures)
        for scenario in scenarios:
            for question in scenario["questions"]:
                self.assertTrue(question["ask"].strip(), question["key"])
                self.assertNotRegex(question["ask"], DEPENDENT_REFERENCE, question["key"])
                has_options = "options" in question
                has_blanks = "blanks" in question
                self.assertNotEqual(has_options, has_blanks, question["key"])
                if has_options:
                    self.assertEqual(len(question["options"]), 4, question["key"])
                else:
                    self.assertTrue(all(blank["accepted_answers"] for blank in question["blanks"]), question["key"])
                if question["question_style"] == "calculation":
                    self.assertIn(question["calculation_fixture_id"], fixture_ids, question["key"])
                    self.assertEqual(
                        self.fixtures[question["calculation_fixture_id"]]["node_id"],
                        question["node_id"],
                        question["key"],
                    )


if __name__ == "__main__":
    unittest.main()
