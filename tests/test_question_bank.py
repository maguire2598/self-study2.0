import json
import os
import subprocess
import unittest
from copy import deepcopy
from collections import Counter, defaultdict
from pathlib import Path
from unittest.mock import patch

from scripts import generate_collision_pi_a_questions as generator


ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "content" / "courses" / "collision-pi" / "question-bank-a.json"
PUZZLE_PATH = ROOT / "content" / "courses" / "collision-pi" / "knowledge-puzzle.json"
SOURCE_PATH = ROOT / "content" / "courses" / "collision-pi" / "question-source-a.json"
SCHEMA_PATH = ROOT / "schemas" / "objective_question_bank.schema.json"

EXPECTED_QUOTAS = {
    "A1.1": 5, "A1.2": 5, "A1.3": 4,
    "A2.1": 6, "A2.2": 5,
    "A3.1": 8, "A3.2": 10, "A3.3": 12, "A3.4": 8, "A3.5": 10,
    "A4.1": 6, "A4.2": 10, "A4.3": 8,
    "A5.1": 10, "A5.2": 4,
    "A6.1": 10, "A6.2": 5,
    "A7.1": 5, "A7.2": 5, "A7.3": 4,
}


def validate_bank_with_pwsh(bank):
    env = os.environ.copy()
    env["QUESTION_BANK_SCHEMA"] = str(SCHEMA_PATH)
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


class QuestionBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
        cls.questions = cls.bank["questions"]

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
        self.assertTrue(all("question_style" in q for q in self.questions))
        styles = Counter(q["question_style"] for q in self.questions)
        self.assertEqual(styles, Counter({"scenario": 88, "calculation": 8, "concise": 44}))
        self.assertEqual(len({q["scenario_id"] for q in self.questions if q.get("scenario_id")}), 13)
        self.assertTrue(all(
            q.get("calculation_fixture_id")
            for q in self.questions
            if q["question_style"] == "calculation"
        ))

    def test_prompts_and_node_titles_match_authored_contract(self):
        puzzle = json.loads(PUZZLE_PATH.read_text(encoding="utf-8"))
        titles = {
            node["id"]: node["title"]
            for node in puzzle["nodes"]
            if node["board"] == "A" and node["depth"] == 2
        }
        banned = ("关于“", "判断“", "下列哪项最符合“")
        for question in self.questions:
            self.assertIn(question["node_id"], titles)
            self.assertEqual(question["node_title"], titles[question["node_id"]])
            self.assertFalse(
                any(phrase in question["prompt"] for phrase in banned),
                question["prompt"],
            )

    def test_answers_and_explanations_are_complete(self):
        for question in self.questions:
            self.assertEqual(question["assessment_kind"], "objective")
            self.assertTrue(question["prompt"].strip())
            self.assertTrue(question["explanation"].strip())
            if question["question_type"] in {"single_choice", "multiple_choice"}:
                expected_count = 1 if question["question_type"] == "single_choice" else 2
                self.assertEqual(len(question["correct_answers"]), expected_count)
                self.assertEqual(len(question["options"]), 4)
            else:
                self.assertGreaterEqual(len(question["blanks"]), 1)
                self.assertTrue(all(blank["accepted_answers"] for blank in question["blanks"]))

    def test_ids_and_prompts_are_unique(self):
        ids = [question["id"] for question in self.questions]
        self.assertEqual(len(ids), len(set(ids)))
        prompts_by_node = defaultdict(list)
        for question in self.questions:
            prompts_by_node[question["node_id"]].append(question["prompt"])
        for node_id, prompts in prompts_by_node.items():
            self.assertEqual(len(prompts), len(set(prompts)), node_id)

    def test_delivery_and_assessment_policy(self):
        self.assertFalse(self.bank["status_assessment"]["enabled"])
        policy = self.bank["delivery_policy"]
        self.assertFalse(policy["reveal_answer_after_wrong"])
        self.assertEqual(policy["wrong_answer_action"], "error_followup_agent")
        self.assertEqual(policy["correct_answer_actions"], ["next_question", "error_followup_agent"])

    def test_source_expansion_preserves_order_prompts_and_answers(self):
        self.assertTrue(hasattr(generator, "expand_questions"), "generator must expose expand_questions")
        source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
        puzzle = json.loads(PUZZLE_PATH.read_text(encoding="utf-8"))
        authored = [
            (scenario, question)
            for scenario in source["scenarios"]
            for question in scenario["questions"]
        ] + [(None, question) for question in source["standalone_questions"]]
        expanded = generator.expand_questions(source, puzzle)

        expected_ids = [
            f"cp-{question['node_id'].lower().replace('.', '-')}-{question['key']}"
            for _, question in authored
        ]
        self.assertEqual([question["id"] for question in expanded], expected_ids)
        for item, (scenario, question) in zip(expanded, authored, strict=True):
            expected_prompt = (
                question["prompt"]
                if scenario is None
                else f"{scenario['context']}\n\n{question['ask']}"
            )
            self.assertEqual(item["prompt"], expected_prompt)
            if "options" in question:
                correctness = {option["text"]: option["correct"] for option in question["options"]}
                expected_answers = {
                    option["id"] for option in item["options"] if correctness[option["text"]]
                }
                self.assertEqual(set(item["correct_answers"]), expected_answers)
            else:
                self.assertEqual(item["blanks"], question["blanks"])

    def test_expansion_rejects_non_assessed_node(self):
        self.assertTrue(hasattr(generator, "expand_questions"), "generator must expose expand_questions")
        puzzle = json.loads(PUZZLE_PATH.read_text(encoding="utf-8"))
        source = {
            "scenarios": [],
            "standalone_questions": [{"node_id": "A1", "key": "invalid-node"}],
        }
        with self.assertRaisesRegex(ValueError, "question references non-assessed node: A1"):
            generator.expand_questions(source, puzzle)

    def test_build_bank_rejects_quota_mismatch(self):
        self.assertTrue(hasattr(generator, "load_inputs"), "generator must expose load_inputs")
        source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
        puzzle = json.loads(PUZZLE_PATH.read_text(encoding="utf-8"))
        invalid_source = deepcopy(source)
        invalid_source["node_quotas"]["A1.1"] += 1
        with patch.object(generator, "load_inputs", return_value=(invalid_source, puzzle)):
            with self.assertRaisesRegex(ValueError, "question quota mismatch"):
                generator.build_bank()

    def test_formal_schema_requires_question_style(self):
        candidate = generator.build_bank()
        valid = validate_bank_with_pwsh(candidate)
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        candidate["questions"][0].pop("question_style")
        result = validate_bank_with_pwsh(candidate)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_formal_schema_accepts_the_140_question_contract(self):
        candidate = deepcopy(self.bank)
        result = validate_bank_with_pwsh(candidate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_schema_rejects(self, candidate, label):
        result = validate_bank_with_pwsh(candidate)
        self.assertNotEqual(result.returncode, 0, f"{label}: {result.stdout}{result.stderr}")

    def mutated_question(self, *, question_type=None, question_style=None):
        candidate = deepcopy(self.bank)
        question = next(
            question
            for question in candidate["questions"]
            if (question_type is None or question["question_type"] == question_type)
            and (question_style is None or question["question_style"] == question_style)
        )
        return candidate, question

    def test_formal_schema_routes_question_payloads(self):
        mutations = []

        candidate, question = self.mutated_question(question_type="single_choice")
        question.pop("options")
        question.pop("correct_answers")
        mutations.append(("single choice without payload", candidate))

        candidate, question = self.mutated_question(question_type="multi_blank")
        question.pop("blanks")
        mutations.append(("multi blank without blanks", candidate))

        candidate, question = self.mutated_question(question_type="single_choice")
        question["blanks"] = [{"id": "unexpected", "accepted_answers": ["x"]}]
        mutations.append(("choice with blanks", candidate))

        candidate, question = self.mutated_question(question_type="multi_blank")
        question["options"] = [
            {"id": option_id, "text": option_id}
            for option_id in ("A", "B", "C", "D")
        ]
        question["correct_answers"] = ["A"]
        mutations.append(("multi blank with choice payload", candidate))

        for label, candidate in mutations:
            with self.subTest(label=label):
                self.assert_schema_rejects(candidate, label)

    def test_formal_schema_locks_choice_cardinality_and_ids(self):
        mutations = []

        candidate, question = self.mutated_question(question_type="single_choice")
        question["correct_answers"] = ["A", "B"]
        mutations.append(("single choice with two answers", candidate))

        candidate, question = self.mutated_question(question_type="multiple_choice")
        question["correct_answers"] = ["A"]
        mutations.append(("multiple choice with one answer", candidate))

        candidate, question = self.mutated_question(question_type="multiple_choice")
        question["correct_answers"] = ["A", "A"]
        mutations.append(("multiple choice with duplicate answers", candidate))

        candidate, question = self.mutated_question(question_type="single_choice")
        question["options"].pop()
        mutations.append(("choice with three options", candidate))

        candidate, question = self.mutated_question(question_type="single_choice")
        question["options"][0]["id"] = "D"
        mutations.append(("choice without strict A-B-C-D ids", candidate))

        for label, candidate in mutations:
            with self.subTest(label=label):
                self.assert_schema_rejects(candidate, label)

    def test_formal_schema_requires_question_metadata(self):
        for field in ("difficulty", "event_stage", "variant_axis"):
            with self.subTest(field=field):
                candidate = deepcopy(self.bank)
                candidate["questions"][0].pop(field)
                self.assert_schema_rejects(candidate, f"question without {field}")

    def test_formal_schema_requires_calculation_fixture(self):
        candidate, question = self.mutated_question(question_style="calculation")
        question.pop("calculation_fixture_id")
        self.assert_schema_rejects(candidate, "calculation without fixture")


if __name__ == "__main__":
    unittest.main()
