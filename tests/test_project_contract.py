import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProjectContractTests(unittest.TestCase):
    def test_required_project_files_exist(self):
        required = [
            "AGENTS.md",
            "README.md",
            "docs/roadmap.md",
            "docs/decisions/conversation-decisions.md",
            "docs/product/error-followup-agent.md",
            "content/courses/collision-pi/knowledge-puzzle.json",
            "content/courses/collision-pi/question-bank-a.json",
            "authoring/collision-pi-question-editor.html",
            "schemas/objective_question_bank.schema.json",
        ]
        for relative_path in required:
            self.assertTrue((ROOT / relative_path).is_file(), relative_path)

    def test_knowledge_puzzle_has_approved_node_counts(self):
        data = json.loads(
            (ROOT / "content/courses/collision-pi/knowledge-puzzle.json").read_text(encoding="utf-8")
        )
        counts = Counter(node["board"] for node in data["nodes"])
        self.assertEqual(counts, Counter({"A": 27, "B": 30, "C": 46, "D": 36}))
        self.assertEqual(len(data["nodes"]), 139)

    def test_a_question_bank_contract(self):
        bank = json.loads(
            (ROOT / "content/courses/collision-pi/question-bank-a.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(bank["questions"]), 192)
        self.assertFalse(bank["status_assessment"]["enabled"])
        self.assertFalse(bank["delivery_policy"]["reveal_answer_after_wrong"])
        self.assertEqual(bank["delivery_policy"]["wrong_answer_action"], "error_followup_agent")


if __name__ == "__main__":
    unittest.main()
