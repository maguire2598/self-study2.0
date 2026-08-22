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
        self.assertEqual(len(self.nodes), 139)
        self.assertEqual(
            Counter(node["board"] for node in self.nodes),
            Counter({"A": 27, "B": 30, "C": 46, "D": 36}),
        )

    def test_a_has_seven_stages_and_twenty_assessed_nodes(self):
        a_nodes = [node for node in self.nodes if node["board"] == "A"]
        self.assertEqual(sum(node["depth"] == 1 for node in a_nodes), 7)
        self.assertEqual(sum(node["depth"] == 2 for node in a_nodes), 20)
        self.assertEqual(
            [node["id"] for node in a_nodes if node["depth"] == 1],
            ["A1", "A2", "A3", "A4", "A5", "A6", "A7"],
        )

    def test_a_records_match_approved_contract(self):
        expected = [
            {"id": "A1", "depth": 1, "parent": None, "title": "场景、初态与记录", "role": "核心", "summary": "建立碰撞场景的对象、初始状态、方向和事件记录框架。"},
            {"id": "A1.1", "depth": 2, "parent": "A1", "title": "对象、空间顺序与初速度", "role": "核心", "summary": "识别物块、墙面及其左右顺序，并读出各对象的初速度。"},
            {"id": "A1.2", "depth": 2, "parent": "A1", "title": "两类碰撞与计数口径", "role": "核心", "summary": "区分物块间碰撞和物块撞墙，统一碰撞次数的计数口径。"},
            {"id": "A1.3", "depth": 2, "parent": "A1", "title": "方向约定与状态记录", "role": "工具", "summary": "选定正方向，用带符号速度和状态表记录事件前后状态。"},
            {"id": "A2", "depth": 1, "parent": None, "title": "模型条件与变量", "role": "核心", "summary": "明确理想模型、可变条件和现实偏差，判断结论的适用范围。"},
            {"id": "A2.1", "depth": 2, "parent": "A2", "title": "理想模型与现实偏差", "role": "核心", "summary": "比较光滑、完全弹性、固定墙等理想条件与摩擦、形变等现实因素。"},
            {"id": "A2.2", "depth": 2, "parent": "A2", "title": "质量比与控制变量", "role": "工具", "summary": "用质量比组织参数，并在比较情景时只改变指定变量。"},
            {"id": "A3", "depth": 1, "parent": None, "title": "单次物块碰撞", "role": "核心", "summary": "分析一次一维物块碰撞是否发生及碰撞前后的物理量变化。"},
            {"id": "A3.1", "depth": 2, "parent": "A3", "title": "是否发生碰撞：位置与相对速度", "role": "核心", "summary": "结合空间顺序和相对速度判断两物块是否会接近并碰撞。"},
            {"id": "A3.2", "depth": 2, "parent": "A3", "title": "等质量弹性碰撞", "role": "核心", "summary": "掌握等质量一维完全弹性碰撞中的速度交换及方向判断。"},
            {"id": "A3.3", "depth": 2, "parent": "A3", "title": "不等质量弹性碰撞", "role": "核心", "summary": "根据质量比和初速度判断不等质量弹性碰撞后的速度大小与方向。"},
            {"id": "A3.4", "depth": 2, "parent": "A3", "title": "摩擦与非弹性改变什么", "role": "边界", "summary": "判断摩擦和非弹性因素会改变哪些守恒条件、速度与能量结论。"},
            {"id": "A3.5", "depth": 2, "parent": "A3", "title": "单体与系统的动量和动能", "role": "核心", "summary": "区分单个物块的动量、动能变化与所选系统的总量守恒。"},
            {"id": "A4", "depth": 1, "parent": None, "title": "连续碰撞与事件链", "role": "核心", "summary": "按时间顺序连接物块碰撞、撞墙和再次碰撞等事件。"},
            {"id": "A4.1", "depth": 2, "parent": "A4", "title": "第一次碰撞如何引出撞墙", "role": "核心", "summary": "根据第一次物块碰撞后的速度判断小物块是否以及何时撞墙。"},
            {"id": "A4.2", "depth": 2, "parent": "A4", "title": "墙反弹后能否再次追上", "role": "核心", "summary": "比较墙反弹后的方向、位置和速度，判断物块能否再次相撞。"},
            {"id": "A4.3", "depth": 2, "parent": "A4", "title": "事件链与状态表", "role": "工具", "summary": "用逐事件状态表追踪位置关系、速度和累计碰撞次数。"},
            {"id": "A5", "depth": 1, "parent": None, "title": "碰撞链的结束", "role": "核心", "summary": "识别不会再发生后续碰撞的终态，并区分事件结束与运动停止。"},
            {"id": "A5.1", "depth": 2, "parent": "A5", "title": "终止判据 vM≥vm≥0", "role": "核心", "summary": "在规定位置与正方向下，用速度排序判断碰撞链是否终止。"},
            {"id": "A5.2", "depth": 2, "parent": "A5", "title": "碰撞结束不等于停止运动", "role": "边界", "summary": "说明不再碰撞只表示物块彼此远离，不代表所有物块静止。"},
            {"id": "A6", "depth": 1, "parent": None, "title": "碰撞次数与 π", "role": "核心", "summary": "观察质量比变化时的碰撞次数规律及其与 π 数字的联系。"},
            {"id": "A6.1", "depth": 2, "parent": "A6", "title": "质量比、碰撞次数与 100ⁿ", "role": "核心", "summary": "比较质量比为 100 的幂时的碰撞次数，并识别其 π 位数模式。"},
            {"id": "A6.2", "depth": 2, "parent": "A6", "title": "观察规律、证明与近似边界", "role": "边界", "summary": "区分数值观察、数学证明和近似结论，关注整数边界条件。"},
            {"id": "A7", "depth": 1, "parent": None, "title": "组合情景拓展", "role": "拓展", "summary": "将碰撞分析迁移到含斜面、弹簧和多阶段系统边界的情景。"},
            {"id": "A7.1", "depth": 2, "parent": "A7", "title": "斜面与碰撞的分段过程", "role": "拓展", "summary": "分开分析斜面运动、短时碰撞和碰后运动各阶段。"},
            {"id": "A7.2", "depth": 2, "parent": "A7", "title": "弹簧与碰撞的分段过程", "role": "拓展", "summary": "分开分析短时碰撞与随后弹簧压缩或回弹过程。"},
            {"id": "A7.3", "depth": 2, "parent": "A7", "title": "组合系统的边界与守恒条件", "role": "工具", "summary": "针对每个阶段选择研究系统，并判断动量或机械能守恒条件。"},
        ]
        a_nodes = [node for node in self.nodes if node["board"] == "A"]
        actual = [
            {
                "id": node["id"],
                "depth": node["depth"],
                "parent": node.get("parent"),
                "title": node["title"],
                "role": node["role"],
                "summary": node["summary"],
            }
            for node in a_nodes
        ]
        self.assertEqual(actual, expected)
        for node in a_nodes:
            if node["depth"] == 1:
                self.assertNotIn("parent", node)
            else:
                self.assertEqual(node["parent"], node["id"].split(".")[0])

    def test_markdown_is_generated_from_json(self):
        from scripts.build_collision_pi_knowledge_puzzle import render_markdown

        expected = PUZZLE_PATH.with_suffix(".md").read_text(encoding="utf-8")
        self.assertEqual(render_markdown(self.puzzle), expected)

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
