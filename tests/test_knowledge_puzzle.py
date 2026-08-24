import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUZZLE_PATH = ROOT / "content" / "courses" / "collision-pi" / "knowledge-puzzle.json"
PUZZLE_SCHEMA_PATH = ROOT / "schemas" / "knowledge_puzzle.schema.json"

EXPECTED_B_IDS = (
    "B1", "B1.1", "B1.2", "B1.3", "B1.4",
    "B2", "B2.1", "B2.2", "B2.3", "B2.4",
    "B3", "B3.1", "B3.2", "B3.3", "B3.4", "B3.5",
    "B4", "B4.1", "B4.2", "B4.3", "B4.4", "B4.5",
    "B5", "B5.1", "B5.2", "B5.3", "B5.4",
)

EXPECTED_B_QUOTAS = {
    "B1.1": 6, "B1.2": 6, "B1.3": 6, "B1.4": 6,
    "B2.1": 8, "B2.2": 10, "B2.3": 8, "B2.4": 6,
    "B3.1": 6, "B3.2": 8, "B3.3": 8, "B3.4": 10, "B3.5": 6,
    "B4.1": 10, "B4.2": 12, "B4.3": 10, "B4.4": 8, "B4.5": 6,
    "B5.1": 8, "B5.2": 8, "B5.3": 8, "B5.4": 4,
}

EXPECTED_B_RECORDS = (
    {"id": "B1", "parent": None, "depth": 1, "title": "先把物理量记清", "role": "核心", "summary": "用有方向的动量、冲量和无方向的动能准确记录状态与变化。"},
    {"id": "B1.1", "parent": "B1", "depth": 2, "title": "动量 p=mv 与正负方向", "role": "核心", "summary": "规定正方向后，用 p=mv 记录带符号的动量。"},
    {"id": "B1.2", "parent": "B1", "depth": 2, "title": "冲量与动量变化 Δp", "role": "核心", "summary": "用 I=Δp 连接作用时间内的合外力冲量和动量变化。"},
    {"id": "B1.3", "parent": "B1", "depth": 2, "title": "动能 ½mv² 与能量转化", "role": "核心", "summary": "动能由速率平方决定；碰撞中可在动能、内能、声能和形变能之间转化。"},
    {"id": "B1.4", "parent": "B1", "depth": 2, "title": "单体量与系统总量", "role": "核心", "summary": "区分单个物体的量与所选系统的总量，避免把局部不变误当总量守恒。"},
    {"id": "B2", "parent": None, "depth": 1, "title": "先选系统，再谈守恒", "role": "核心", "summary": "研究任何守恒前先确定系统、时段和外界作用。"},
    {"id": "B2.1", "parent": "B2", "depth": 2, "title": "研究系统与时间区间", "role": "核心", "summary": "先明确研究对象和时间区间，系统边界可随事件改变。"},
    {"id": "B2.2", "parent": "B2", "depth": 2, "title": "外冲量与动量守恒条件", "role": "核心", "summary": "所选系统在研究时段内外部总冲量可忽略时，总动量守恒。"},
    {"id": "B2.3", "parent": "B2", "depth": 2, "title": "弹性、非弹性与动能条件", "role": "核心", "summary": "弹性碰撞保持系统总动能；非弹性碰撞只在满足外冲量条件时保留总动量守恒。"},
    {"id": "B2.4", "parent": "B2", "depth": 2, "title": "撞墙、摩擦和现实边界", "role": "边界", "summary": "撞墙、摩擦、可动墙和耗散会改变外冲量或能量条件，需重新选择系统与规律。"},
    {"id": "B3", "parent": None, "depth": 1, "title": "建立一次碰撞的约束", "role": "核心", "summary": "把一维碰撞的物理条件翻译成可联立的方程关系。"},
    {"id": "B3.1", "parent": "B3", "depth": 2, "title": "碰前碰后变量与符号", "role": "核心", "summary": "统一质量、位置、碰前和碰后速度及正方向，并确认两物体确会相碰。"},
    {"id": "B3.2", "parent": "B3", "depth": 2, "title": "两物体动量守恒式", "role": "核心", "summary": "对短碰阶段的两物体系统写带符号的总动量守恒式。"},
    {"id": "B3.3", "parent": "B3", "depth": 2, "title": "两物体动能守恒式", "role": "核心", "summary": "完全弹性条件下写两物体碰前后总动能相等式。"},
    {"id": "B3.4", "parent": "B3", "depth": 2, "title": "相对速度反向关系", "role": "核心", "summary": "由两守恒式得到分离相对速度等于接近相对速度，方向反向。"},
    {"id": "B3.5", "parent": "B3", "depth": 2, "title": "恢复系数 e 与弹性程度", "role": "拓展", "summary": "用恢复系数统一描述弹性程度；e=1 为完全弹性，0≤e<1 为非完全弹性。"},
    {"id": "B4", "parent": None, "depth": 1, "title": "联立求解并检查物理解", "role": "核心", "summary": "从方程得到速度结果，并用特例、极限和守恒回代检验。"},
    {"id": "B4.1", "parent": "B4", "depth": 2, "title": "消元与平方差分解", "role": "工具", "summary": "用代入消元或平方差分解，把两个守恒式化为可解的一次关系。"},
    {"id": "B4.2", "parent": "B4", "depth": 2, "title": "一维弹性碰撞速度通式", "role": "核心", "summary": "得到任意质量和初速度的一维弹性碰撞速度通式，并明确适用条件。"},
    {"id": "B4.3", "parent": "B4", "depth": 2, "title": "等质量与典型质量比", "role": "核心", "summary": "等质量速度交换、轻撞重反弹和重撞轻加速是通式的典型特例。"},
    {"id": "B4.4", "parent": "B4", "depth": 2, "title": "方向、极限与解的筛选", "role": "核心", "summary": "结合方向、接近和分离条件及质量极限，排除平凡解或非物理解。"},
    {"id": "B4.5", "parent": "B4", "depth": 2, "title": "守恒回代与结果检验", "role": "工具", "summary": "将结果回代动量、动能、相对速度和量纲，检查计算与模型一致。"},
    {"id": "B5", "parent": None, "depth": 1, "title": "把一次碰撞接成事件链", "role": "核心", "summary": "用一次碰撞规则构造多次碰撞状态机，并进入几何表示。"},
    {"id": "B5.1", "parent": "B5", "depth": 2, "title": "碰撞、撞墙与自由运动更新", "role": "核心", "summary": "把物块碰撞、固定墙反射和碰撞间匀速运动写成独立状态更新规则。"},
    {"id": "B5.2", "parent": "B5", "depth": 2, "title": "下一事件判断与状态递推", "role": "核心", "summary": "根据位置和相对速度判断下一事件，并用状态表或递推记录连续更新。"},
    {"id": "B5.3", "parent": "B5", "depth": 2, "title": "终止判据、计数与极限状态", "role": "核心", "summary": "用无后续接触条件判断碰撞链终止，处理大物块停下等极限状态和计数。"},
    {"id": "B5.4", "parent": "B5", "depth": 2, "title": "直线—椭圆状态图，衔接 C", "role": "衔接", "summary": "将动量守恒画成直线、动能守恒画成椭圆；碰前碰后对应两个交点。"},
)


class KnowledgePuzzleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.puzzle = json.loads(PUZZLE_PATH.read_text(encoding="utf-8"))
        cls.nodes = cls.puzzle["nodes"]

    def test_exact_node_and_board_counts(self):
        self.assertEqual(len(self.nodes), 136)
        self.assertEqual(
            Counter(node["board"] for node in self.nodes),
            Counter({"A": 27, "B": 27, "C": 46, "D": 36}),
        )

    def test_b_has_five_stages_and_twenty_two_assessed_nodes(self):
        b_nodes = [node for node in self.nodes if node["board"] == "B"]
        self.assertEqual(tuple(node["id"] for node in b_nodes), EXPECTED_B_IDS)
        self.assertEqual(sum(node["depth"] == 1 for node in b_nodes), 5)
        self.assertEqual(sum(node["depth"] == 2 for node in b_nodes), 22)

    def test_b_records_match_approved_contract(self):
        b_nodes = [node for node in self.nodes if node["board"] == "B"]
        actual = tuple(
            {
                "id": node["id"],
                "parent": node.get("parent"),
                "depth": node["depth"],
                "title": node["title"],
                "role": node["role"],
                "summary": node["summary"],
            }
            for node in b_nodes
        )
        self.assertEqual(actual, EXPECTED_B_RECORDS)

    def test_b_question_quotas_total_168(self):
        self.assertEqual(tuple(EXPECTED_B_QUOTAS), EXPECTED_B_IDS[1:5] + EXPECTED_B_IDS[6:10] + EXPECTED_B_IDS[11:16] + EXPECTED_B_IDS[17:22] + EXPECTED_B_IDS[23:])
        self.assertEqual(sum(EXPECTED_B_QUOTAS.values()), 168)

    def test_b_question_assets_only_reference_assessed_nodes(self):
        for pattern in ("question-bank-*.json", "question-source-*.json"):
            for path in (ROOT / "content" / "courses").rglob(pattern):
                data = json.loads(path.read_text(encoding="utf-8"))
                for node_id in self._node_ids(data):
                    if node_id.startswith("B"):
                        self.assertIn(node_id, EXPECTED_B_QUOTAS, path)

    @staticmethod
    def _node_ids(value):
        if isinstance(value, dict):
            for key, nested in value.items():
                if key == "node_id":
                    yield nested
                yield from KnowledgePuzzleTests._node_ids(nested)
        elif isinstance(value, list):
            for nested in value:
                yield from KnowledgePuzzleTests._node_ids(nested)

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
        allowed_roles = {"核心", "工具", "选修", "边界", "拓展", "衔接"}
        for node in self.nodes:
            self.assertIn(node["role"], allowed_roles)
            self.assertIn(node["board"], {"A", "B", "C", "D"})
            self.assertIn(node["depth"], {1, 2})
            self.assertTrue(node["title"].strip())
            self.assertTrue(node["summary"].strip())

    def test_schema_accepts_handoff_role(self):
        schema = json.loads(PUZZLE_SCHEMA_PATH.read_text(encoding="utf-8"))
        roles = schema["properties"]["nodes"]["items"]["properties"]["role"]["enum"]
        self.assertIn("衔接", roles)

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
