import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUZZLE_PATH = ROOT / "content" / "courses" / "collision-pi" / "knowledge-puzzle.json"


class KnowledgePuzzleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.puzzle = json.loads(PUZZLE_PATH.read_text(encoding="utf-8"))
        cls.nodes = cls.puzzle["nodes"]

    def test_exact_node_and_board_counts(self):
        self.assertEqual(len(self.nodes), 144)
        self.assertEqual(
            Counter(node["board"] for node in self.nodes),
            Counter({"A": 32, "B": 30, "C": 46, "D": 36}),
        )

    def test_node_ids_are_unique(self):
        ids = [node["id"] for node in self.nodes]
        self.assertEqual(len(ids), len(set(ids)))

    def test_roles_and_required_fields(self):
        allowed_roles = {"核心", "工具", "选修", "边界", "拓展"}
        for node in self.nodes:
            self.assertIn(node["role"], allowed_roles)
            self.assertIn(node["board"], {"A", "B", "C", "D"})
            self.assertIn(node["depth"], {1, 2})
            self.assertTrue(node["title"].strip())
            self.assertTrue(node["summary"].strip())

    def test_light_reflection_is_elective(self):
        c9 = next(node for node in self.nodes if node["id"] == "C9")
        self.assertEqual(c9["role"], "选修")
        self.assertIn("光线反射", c9["title"])

    def test_d_contains_calculation_and_pi_digit_nodes(self):
        d_nodes = [node for node in self.nodes if node["board"] == "D"]
        combined = " ".join(f"{node['title']} {node['summary']}" for node in d_nodes)
        self.assertIn("碰撞次数", combined)
        self.assertIn("π", combined)
        self.assertIn("位", combined)


if __name__ == "__main__":
    unittest.main()
