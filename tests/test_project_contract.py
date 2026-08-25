import json
import unittest
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts import build_collision_pi_question_editor as editor_builder


ROOT = Path(__file__).resolve().parents[1]
CURRENT_FILES = (
    ROOT / "AGENTS.md",
    ROOT / "README.md",
    ROOT / "docs/roadmap.md",
    ROOT / "docs/decisions/conversation-decisions.md",
)
CURRENT_CONTRACT = (
    "《碰撞与π》知识拼图共 139 个节点：A=27、B=30、C=46、D=36。",
    "A 板块有 20 个承载题目的二级节点，共 140 道客观题。",
    "题量按知识重要性分配，题库包含 13 个场景题组和 8 道计算题。",
)


class ProjectContractTests(unittest.TestCase):
    def test_current_docs_do_not_claim_retired_a_contract(self):
        retired = [
            "144 个知识节点",
            "144 节点知识拼图",
            "A 板块 192 道",
            "A 板块 192 题",
            "A 板块 32 个节点",
            "每个知识节点 6 题",
            "32 个节点 × 6 题",
        ]
        for path in CURRENT_FILES:
            text = path.read_text(encoding="utf-8")
            for phrase in retired:
                self.assertNotIn(phrase, text, f"{path}: {phrase}")

    def test_current_docs_state_exact_current_contract(self):
        for path in CURRENT_FILES:
            text = path.read_text(encoding="utf-8")
            for statement in CURRENT_CONTRACT:
                self.assertIn(statement, text, f"{path}: {statement}")

    def test_checked_in_question_editor_matches_builder(self):
        expected = editor_builder.build()
        actual = (ROOT / "authoring/collision-pi-question-editor.html").read_text(
            encoding="utf-8"
        )
        self.assertEqual(actual, expected)

        scripts = [
            script.split(">", 1)[1].rsplit("</script>", 1)[0]
            for script in actual.split("<script")
            if "</script>" in script
        ]
        banks = json.loads(scripts[0])
        self.assertEqual(set(banks), {"A", "B"})
        self.assertEqual(len(banks["A"]["questions"]), 140)
        self.assertEqual(len(banks["B"]["questions"]), 168)

    def test_editor_builder_escapes_script_terminators_in_question_data(self):
        """A schema-valid prompt must not close the embedded JSON script element."""
        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            template = temp_root / "editor.html"
            bank_a = temp_root / "a.json"
            bank_b = temp_root / "b.json"
            template.write_text(
                '<script type="application/json">__QUESTION_BANKS_JSON__</script>',
                encoding="utf-8",
            )
            bank_a.write_text(
                json.dumps({"questions": [{"prompt": "</script><script>sentinel()</script>"}]}),
                encoding="utf-8",
            )
            bank_b.write_text(json.dumps({"questions": []}), encoding="utf-8")
            with patch.object(editor_builder, "TEMPLATE", template), patch.object(
                editor_builder, "BANKS", {"A": bank_a, "B": bank_b}
            ):
                generated = editor_builder.build()

        self.assertIn(r"\u003c/script>\u003cscript>sentinel()\u003c/script>", generated)
        self.assertNotIn("</script><script>sentinel()</script>", generated)

    def test_required_project_files_exist(self):
        required = [
            "AGENTS.md",
            "README.md",
            "docs/roadmap.md",
            "docs/decisions/conversation-decisions.md",
            "docs/product/error-followup-agent.md",
            "content/courses/collision-pi/knowledge-puzzle.json",
            "content/courses/collision-pi/question-bank-a.json",
            "content/courses/collision-pi/question-bank-b.json",
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
        self.assertEqual(counts, Counter({"A": 27, "B": 27, "C": 46, "D": 36}))
        self.assertEqual(len(data["nodes"]), 136)

    def test_a_question_bank_contract(self):
        bank = json.loads(
            (ROOT / "content/courses/collision-pi/question-bank-a.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(bank["questions"]), 140)
        self.assertEqual(bank["version"], "2.0.0")
        self.assertFalse(bank["status_assessment"]["enabled"])
        self.assertFalse(bank["delivery_policy"]["reveal_answer_after_wrong"])
        self.assertEqual(bank["delivery_policy"]["wrong_answer_action"], "error_followup_agent")

    def test_b_question_bank_contract(self):
        bank = json.loads(
            (ROOT / "content/courses/collision-pi/question-bank-b.json").read_text(encoding="utf-8")
        )
        self.assertEqual(bank["section_id"], "B")
        self.assertEqual(len(bank["questions"]), 168)
        self.assertEqual(len(bank["question_count_by_node"]), 22)
        self.assertFalse(bank["status_assessment"]["enabled"])
        self.assertFalse(bank["delivery_policy"]["reveal_answer_after_wrong"])


if __name__ == "__main__":
    unittest.main()
