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

    def test_scenario_and_standalone_text_fields_are_separate(self):
        for question in self.scenario_questions:
            self.assertTrue(question["ask"].strip())
            self.assertNotIn("prompt", question)
        for question in self.standalone:
            self.assertTrue(question["prompt"].strip())
            self.assertNotIn("ask", question)


if __name__ == "__main__":
    unittest.main()
