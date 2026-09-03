import json
import unittest
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BANK_PATH = ROOT / "content" / "courses" / "collision-pi" / "question-bank-a.json"
PUZZLE_PATH = ROOT / "content" / "courses" / "collision-pi" / "knowledge-puzzle.json"


class QuestionBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
        cls.questions = cls.bank["questions"]

    def test_exact_question_count_and_node_distribution(self):
        self.assertEqual(len(self.questions), 192)
        per_node = defaultdict(Counter)
        for question in self.questions:
            per_node[question["node_id"]][question["question_type"]] += 1
        expected = Counter({"single_choice": 3, "multiple_choice": 2, "multi_blank": 1})
        self.assertEqual(len(per_node), 32)
        for node_id, counts in per_node.items():
            self.assertEqual(counts, expected, node_id)

    def test_bank_nodes_equal_puzzle_a_nodes(self):
        puzzle = json.loads(PUZZLE_PATH.read_text(encoding="utf-8"))
        expected = {node["id"] for node in puzzle["nodes"] if node["board"] == "A"}
        actual = {question["node_id"] for question in self.questions}
        self.assertEqual(actual, expected)

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
                self.assertGreaterEqual(len(question["blanks"]), 2)
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


if __name__ == "__main__":
    unittest.main()
