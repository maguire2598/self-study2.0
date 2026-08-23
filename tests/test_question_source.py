import copy
import json
import math
import os
import subprocess
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content/courses/collision-pi/question-source-a.json"
SCHEMA = ROOT / "schemas/objective_question_source.schema.json"

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

EXPECTED_SCENARIO_IDS = (
    "SC-A3-RELATIVE", "SC-A3-EQUAL", "SC-A3-UNEQUAL", "SC-A3-LARGE-RATIO",
    "SC-A3-NONIDEAL", "SC-A3-CONSERVATION", "SC-A4-FIRST-WALL",
    "SC-A4-CHASE", "SC-A4-STATE-1", "SC-A4-STATE-3", "SC-A7-INCLINE",
    "SC-A7-SPRING", "SC-A7-BOUNDARY",
)

EXPECTED_SCENARIO_NODE_COUNTS = {
    "SC-A3-RELATIVE": {"A3.1": 8},
    "SC-A3-EQUAL": {"A3.2": 10},
    "SC-A3-UNEQUAL": {"A3.3": 8},
    "SC-A3-LARGE-RATIO": {"A3.3": 4},
    "SC-A3-NONIDEAL": {"A3.4": 8},
    "SC-A3-CONSERVATION": {"A3.5": 10},
    "SC-A4-FIRST-WALL": {"A4.1": 6},
    "SC-A4-CHASE": {"A4.2": 10, "A5.1": 5},
    "SC-A4-STATE-1": {"A4.3": 4},
    "SC-A4-STATE-3": {"A4.3": 4, "A5.1": 5},
    "SC-A7-INCLINE": {"A7.1": 5},
    "SC-A7-SPRING": {"A7.2": 5},
    "SC-A7-BOUNDARY": {"A7.3": 4},
}

EXPECTED_SOURCES = {
    "video-main": "sources/theory/弹性碰撞与π.txt",
    "openstax-collision": "https://openstax.org/books/college-physics/pages/8-4-elastic-collisions-in-one-dimension",
    "openstax-inelastic": "https://openstax.org/books/physics/pages/8-3-elastic-and-inelastic-collisions",
    "openstax-incline": "https://openstax.org/books/college-physics-2e/pages/7-3-gravitational-potential-energy",
    "openstax-spring": "https://openstax.org/books/college-physics-2e/pages/7-4-conservative-forces-and-potential-energy",
}

EXPECTED_FIXTURES = {
    "CAL-A3-EQ-01": {
        "id": "CAL-A3-EQ-01", "node_id": "A3.2", "kind": "elastic_1d",
        "m1": 2, "m2": 2, "u1": -3, "u2": 0, "expected": {"v1": 0, "v2": -3},
    },
    "CAL-A3-EQ-02": {
        "id": "CAL-A3-EQ-02", "node_id": "A3.2", "kind": "elastic_1d",
        "m1": 1, "m2": 1, "u1": 2, "u2": -1, "expected": {"v1": -1, "v2": 2},
    },
    "CAL-A3-UN-01": {
        "id": "CAL-A3-UN-01", "node_id": "A3.3", "kind": "elastic_1d",
        "m1": 3, "m2": 1, "u1": -4, "u2": 0, "expected": {"v1": -2, "v2": -6},
    },
    "CAL-A3-UN-02": {
        "id": "CAL-A3-UN-02", "node_id": "A3.3", "kind": "elastic_1d",
        "m1": 1, "m2": 3, "u1": 4, "u2": 0, "expected": {"v1": -2, "v2": 2},
    },
    "CAL-A3-UN-03": {
        "id": "CAL-A3-UN-03", "node_id": "A3.3", "kind": "elastic_1d",
        "m1": 3, "m2": 1, "u1": 2, "u2": -2, "expected": {"v1": 0, "v2": 4},
    },
    "CAL-A3-DP-01": {
        "id": "CAL-A3-DP-01", "node_id": "A3.5", "kind": "elastic_1d",
        "m1": 3, "m2": 1, "u1": -4, "u2": 0,
        "expected": {"v1": -2, "v2": -6, "delta_p1": 6, "delta_p2": -6},
    },
    "CAL-A7-IN-01": {
        "id": "CAL-A7-IN-01", "node_id": "A7.1", "kind": "incline_speed",
        "g": 10, "height": 1.25, "expected": {"speed": 5},
    },
    "CAL-A7-SP-01": {
        "id": "CAL-A7-SP-01", "node_id": "A7.2", "kind": "spring_compression",
        "mass": 1, "speed": 2, "k": 100, "expected": {"compression": 0.2},
    },
}


def validate_source_with_pwsh(source):
    env = os.environ.copy()
    env["QUESTION_SOURCE_SCHEMA"] = str(SCHEMA)
    script = (
        "$json = [Console]::In.ReadToEnd(); "
        "try { "
        "$valid = $json | Test-Json -SchemaFile $env:QUESTION_SOURCE_SCHEMA -ErrorAction Stop; "
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


class QuestionSourceSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        cls.defs = cls.schema["$defs"]

    def test_schema_locks_quota_source_and_scenario_identities(self):
        quotas = self.schema["properties"]["node_quotas"]
        self.assertEqual(set(quotas["properties"]), set(EXPECTED_QUOTAS))
        self.assertEqual(set(quotas["required"]), set(EXPECTED_QUOTAS))
        self.assertFalse(quotas["additionalProperties"])
        for node_id, quota in EXPECTED_QUOTAS.items():
            self.assertEqual(quotas["properties"][node_id], {"const": quota})

        sources = self.schema["properties"]["source_catalog"]
        self.assertEqual(sources["minItems"], len(EXPECTED_SOURCES))
        self.assertEqual(sources["maxItems"], len(EXPECTED_SOURCES))
        self.assertTrue(sources["uniqueItems"])
        self.assertEqual(set(self.defs["source"]["properties"]["id"]["enum"]), set(EXPECTED_SOURCES))
        self.assertEqual(
            set(self.defs["scenario"]["properties"]["id"]["enum"]),
            CORE_SCENARIOS | EXTENSION_SCENARIOS,
        )

    def test_schema_closes_authored_objects(self):
        self.assertFalse(self.schema["additionalProperties"])
        for definition in (
            "source", "elasticFixture", "inclineFixture", "springFixture",
            "option", "blank", "question", "scenario",
        ):
            self.assertFalse(self.defs[definition]["additionalProperties"], definition)

    def test_schema_pins_source_and_scenario_ids_by_position(self):
        cases = (
            ("source_catalog", tuple(EXPECTED_SOURCES), "#/$defs/source"),
            ("scenarios", EXPECTED_SCENARIO_IDS, "#/$defs/scenario"),
        )
        for property_name, expected_ids, definition_ref in cases:
            collection = self.schema["properties"][property_name]
            self.assertIs(collection["items"], False, property_name)
            self.assertEqual(len(collection["prefixItems"]), len(expected_ids))
            pinned_ids = []
            for item in collection["prefixItems"]:
                self.assertEqual(item["allOf"][0], {"$ref": definition_ref})
                pinned_ids.append(item["allOf"][1]["properties"]["id"]["const"])
            self.assertEqual(tuple(pinned_ids), expected_ids)

    def test_schema_routes_context_specific_text_fields(self):
        scenario_items = self.defs["scenario"]["properties"]["questions"]["items"]
        standalone_items = self.schema["properties"]["standalone_questions"]["items"]
        self.assertEqual(scenario_items, {"$ref": "#/$defs/scenarioQuestion"})
        self.assertEqual(standalone_items, {"$ref": "#/$defs/standaloneQuestion"})

        scenario_question = self.defs["scenarioQuestion"]
        self.assertIn("ask", scenario_question["required"])
        self.assertEqual(scenario_question["not"], {"required": ["prompt"]})
        standalone_question = self.defs["standaloneQuestion"]
        self.assertIn("prompt", standalone_question["required"])
        self.assertEqual(standalone_question["not"], {"required": ["ask"]})

    def test_schema_routes_answer_payloads_and_calculation_fixture(self):
        branches = {
            rule["if"]["properties"].get("question_type", {}).get("const"):
                rule["then"]
            for rule in self.defs["question"]["allOf"]
            if "question_type" in rule.get("if", {}).get("properties", {})
        }
        for question_type in ("single_choice", "multiple_choice"):
            self.assertIn("options", branches[question_type]["required"])
            self.assertEqual(branches[question_type]["not"], {"required": ["blanks"]})
        self.assertIn("blanks", branches["multi_blank"]["required"])
        self.assertEqual(branches["multi_blank"]["not"], {"required": ["options"]})

        calculation_branch = next(
            rule["then"]
            for rule in self.defs["question"]["allOf"]
            if rule.get("if", {}).get("properties", {}).get("question_style", {}).get("const")
            == "calculation"
        )
        self.assertIn("calculation_fixture_id", calculation_branch["required"])


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
        actual_quotas = Counter(
            question["node_id"]
            for question in self.scenario_questions + self.standalone
        )
        self.assertEqual(actual_quotas, Counter(EXPECTED_QUOTAS))
        scenario_ids = {scenario["id"] for scenario in self.source["scenarios"]}
        self.assertEqual(scenario_ids, CORE_SCENARIOS | EXTENSION_SCENARIOS)
        self.assertEqual(len(self.scenario_questions), 96)
        self.assertEqual(len(self.standalone), 44)

    def test_scenario_order_and_family_node_allocations(self):
        scenario_ids = tuple(scenario["id"] for scenario in self.source["scenarios"])
        self.assertEqual(scenario_ids, EXPECTED_SCENARIO_IDS)
        for scenario in self.source["scenarios"]:
            expected = Counter(EXPECTED_SCENARIO_NODE_COUNTS[scenario["id"]])
            actual = Counter(question["node_id"] for question in scenario["questions"])
            self.assertEqual(len(scenario["questions"]), sum(expected.values()), scenario["id"])
            self.assertEqual(actual, expected, scenario["id"])

    def test_style_distribution(self):
        styles = Counter(
            question["question_style"]
            for question in self.scenario_questions + self.standalone
        )
        self.assertEqual(styles, Counter({"scenario": 88, "calculation": 8, "concise": 44}))

    def test_grouped_and_standalone_style_placement(self):
        self.assertTrue(
            all(
                question["question_style"] in {"scenario", "calculation"}
                for question in self.scenario_questions
            )
        )
        self.assertTrue(all(question["question_style"] == "concise" for question in self.standalone))

    def test_draft202012_schema_accepts_source_and_rejects_style_mutations(self):
        valid = validate_source_with_pwsh(self.source)
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

        mutations = []
        grouped_concise = copy.deepcopy(self.source)
        grouped_concise["scenarios"][0]["questions"][0]["question_style"] = "concise"
        mutations.append(("grouped concise", grouped_concise))
        standalone_scenario = copy.deepcopy(self.source)
        standalone_scenario["standalone_questions"][0]["question_style"] = "scenario"
        mutations.append(("standalone scenario", standalone_scenario))

        for label, mutation in mutations:
            with self.subTest(label=label):
                result = validate_source_with_pwsh(mutation)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a6_1_count_questions_pin_canonical_initial_state(self):
        questions = [question for question in self.standalone if question["node_id"] == "A6.1"]
        self.assertEqual(len(questions), 10)
        required_phrases = (
            "墙位于左侧",
            "m 位于墙与物块 M 之间",
            "m 初始静止",
            "M 以非零速度向墙运动",
            "轨道光滑",
            "碰撞完全弹性",
            "墙固定",
            "计一次",
        )
        for question in questions:
            for phrase in required_phrases:
                self.assertIn(phrase, question["prompt"], question["key"])

    def test_calculation_fixtures_are_physically_consistent(self):
        fixtures = self.source["calculation_fixtures"]
        self.assertEqual(len(fixtures), 8)
        self.assertEqual({fixture["id"]: fixture for fixture in fixtures}, EXPECTED_FIXTURES)
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

        fixture_references = Counter(
            question["calculation_fixture_id"]
            for question in self.scenario_questions + self.standalone
            if question["question_style"] == "calculation"
        )
        self.assertEqual(fixture_references, Counter(EXPECTED_FIXTURES.keys()))

    def test_sources_and_question_keys_are_complete(self):
        actual_sources = {
            item["id"]: item["location"]
            for item in self.source["source_catalog"]
        }
        self.assertEqual(len(self.source["source_catalog"]), len(EXPECTED_SOURCES))
        self.assertEqual(actual_sources, EXPECTED_SOURCES)
        for scenario in self.source["scenarios"]:
            keys = [question["key"] for question in scenario["questions"]]
            self.assertEqual(len(keys), len(set(keys)), scenario["id"])
            self.assertTrue(set(scenario["source_refs"]).issubset(EXPECTED_SOURCES))

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

    def test_scenario_and_standalone_text_fields_are_separate(self):
        for question in self.scenario_questions:
            self.assertTrue(question["ask"].strip())
            self.assertNotIn("prompt", question)
        for question in self.standalone:
            self.assertTrue(question["prompt"].strip())
            self.assertNotIn("ask", question)


if __name__ == "__main__":
    unittest.main()
