import json
import os
import subprocess
import unittest
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

from scripts import collision_pi_question_bank as question_bank
from scripts import generate_collision_pi_b_questions as generate_b


ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "content/courses/collision-pi/question-bank-b.json"
SOURCE = ROOT / "content/courses/collision-pi/question-source-b.json"
PUZZLE = ROOT / "content/courses/collision-pi/knowledge-puzzle.json"
SCHEMA = ROOT / "schemas/objective_question_bank.schema.json"
EXPECTED_QUOTAS = {
    "B1.1": 6, "B1.2": 6, "B1.3": 6, "B1.4": 6,
    "B2.1": 8, "B2.2": 10, "B2.3": 8, "B2.4": 6,
    "B3.1": 6, "B3.2": 8, "B3.3": 8, "B3.4": 10, "B3.5": 6,
    "B4.1": 10, "B4.2": 12, "B4.3": 10, "B4.4": 8, "B4.5": 6,
    "B5.1": 8, "B5.2": 8, "B5.3": 8, "B5.4": 4,
}


def validate_bank_with_pwsh(bank):
    env = os.environ.copy()
    env["QUESTION_BANK_SCHEMA"] = str(SCHEMA)
    script = (
        "$json = [Console]::In.ReadToEnd(); "
        "try { "
        "$valid = $json | Test-Json -SchemaFile $env:QUESTION_BANK_SCHEMA -ErrorAction Stop; "
        "if ($valid) { exit 0 } else { exit 1 } "
        "} catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }"
    )
    return subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", script],
        input=json.dumps(bank, ensure_ascii=False),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


class QuestionBankBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads(BANK.read_text(encoding="utf-8"))
        cls.questions = cls.bank["questions"]
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.puzzle = json.loads(PUZZLE.read_text(encoding="utf-8"))

    def test_b_bank_contract(self):
        self.assertEqual(self.bank["section_id"], "B")
        self.assertEqual(self.bank["question_count_by_node"], EXPECTED_QUOTAS)
        self.assertEqual(len(self.bank["questions"]), 168)
        self.assertEqual(
            Counter(q["question_style"] for q in self.bank["questions"]),
            Counter({"scenario": 104, "calculation": 32, "concise": 32}),
        )

    def test_checked_in_b_bank_matches_generator(self):
        self.assertEqual(generate_b.build_bank(), self.bank)

    def test_node_titles_match_assessed_b_puzzle_nodes(self):
        titles = {
            node["id"]: node["title"]
            for node in self.puzzle["nodes"]
            if node["board"] == "B" and node["depth"] == 2
        }
        self.assertEqual(set(question["node_id"] for question in self.questions), set(titles))
        for question in self.questions:
            self.assertEqual(question["node_title"], titles[question["node_id"]])

    def test_ids_and_prompts_are_unique(self):
        ids = [question["id"] for question in self.questions]
        self.assertEqual(len(ids), len(set(ids)))
        prompts_by_node = defaultdict(list)
        for question in self.questions:
            prompts_by_node[question["node_id"]].append(question["prompt"])
        for node_id, prompts in prompts_by_node.items():
            self.assertEqual(len(prompts), len(set(prompts)), node_id)

    def test_delivery_policy_and_answer_payloads_are_complete(self):
        self.assertFalse(self.bank["status_assessment"]["enabled"])
        self.assertEqual(
            self.bank["delivery_policy"],
            {
                "reveal_answer_after_wrong": False,
                "wrong_answer_action": "error_followup_agent",
                "correct_answer_actions": ["next_question", "error_followup_agent"],
            },
        )
        for question in self.questions:
            if question["question_type"] in {"single_choice", "multiple_choice"}:
                self.assertEqual(len(question["options"]), 4)
                expected_answers = 1 if question["question_type"] == "single_choice" else 2
                self.assertEqual(len(question["correct_answers"]), expected_answers)
            else:
                self.assertTrue(question["blanks"])
                self.assertTrue(all(blank["accepted_answers"] for blank in question["blanks"]))

    def test_scenario_metadata_fixture_propagation_and_option_rotation(self):
        authored = [
            (scenario, question)
            for scenario in self.source["scenarios"]
            for question in scenario["questions"]
        ] + [(None, question) for question in self.source["standalone_questions"]]
        self.assertEqual(len({question["scenario_id"] for question in self.questions if "scenario_id" in question}), 15)
        for index, (item, (scenario, question)) in enumerate(zip(self.questions, authored, strict=True)):
            if scenario is None:
                self.assertNotIn("scenario_id", item)
                self.assertNotIn("source_refs", item)
            else:
                self.assertEqual(item["scenario_id"], scenario["id"])
                self.assertEqual(item["source_refs"], scenario["source_refs"])
            if question.get("calculation_fixture_id"):
                self.assertEqual(item["calculation_fixture_id"], question["calculation_fixture_id"])
            else:
                self.assertNotIn("calculation_fixture_id", item)
            if "options" in question:
                rotated = question["options"][index % len(question["options"]):] + question["options"][:index % len(question["options"])]
                self.assertEqual([option["text"] for option in item["options"]], [option["text"] for option in rotated])
                self.assertEqual(
                    item["correct_answers"],
                    ["ABCD"[position] for position, option in enumerate(rotated) if option["correct"]],
                )

    def test_shared_builder_rejects_stage_or_a_node_for_b_source(self):
        for invalid_node in ("B1", "A1.1"):
            with self.subTest(node_id=invalid_node):
                source = deepcopy(self.source)
                source["scenarios"][0]["questions"][0]["node_id"] = invalid_node
                with self.assertRaisesRegex(ValueError, f"question references non-assessed node: {invalid_node}"):
                    question_bank.expand_questions(source, self.puzzle, "B")

    def test_formal_schema_accepts_b_contract_and_rejects_section_mutations(self):
        self.assertEqual(validate_bank_with_pwsh(self.bank).returncode, 0)
        a_bank = json.loads((ROOT / "content/courses/collision-pi/question-bank-a.json").read_text(encoding="utf-8"))
        a_bank["questions"] += deepcopy(a_bank["questions"][:28])
        b_with_a_node = deepcopy(self.bank)
        b_with_a_node["questions"][0]["node_id"] = "A1.1"
        b_missing_quota = deepcopy(self.bank)
        b_missing_quota["question_count_by_node"].pop("B1.1")
        for label, candidate in (
            ("A bank with 168 questions", a_bank),
            ("B bank with an A node", b_with_a_node),
            ("B bank missing a quota", b_missing_quota),
        ):
            with self.subTest(label=label):
                result = validate_bank_with_pwsh(candidate)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
