from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUZZLE = ROOT / "content" / "courses" / "collision-pi" / "knowledge-puzzle.json"
OUTPUT = PUZZLE.with_suffix(".md")
BOARD_TITLES = {
    "A": "碰撞现象与结论",
    "B": "现象与原理",
    "C": "几何化",
    "D": "从模型到π与位数关系",
}


def render_markdown(puzzle: dict) -> str:
    lines = [
        "# 碰撞与π知识拼图",
        "",
        "> 本目录由 `knowledge-puzzle.json` 生成；JSON 是节点单一真相来源。",
        "",
    ]
    for board, title in BOARD_TITLES.items():
        lines.extend([f"## [{board}] {title}", ""])
        for node in (item for item in puzzle["nodes"] if item["board"] == board):
            indent = "  " if node["depth"] == 2 else ""
            role = f" · {node['role']}" if node["role"] != "核心" else ""
            lines.append(f"{indent}- **{node['id']} {node['title']}**{role}：{node['summary']}")
        lines.append("")
    lines.extend([
        "> C9 光线反射法为选修内容。",
        "",
        "> **文档版本**：2.0.0",
        "> **生成日期**：2026-08-22",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    puzzle = json.loads(PUZZLE.read_text(encoding="utf-8"))
    OUTPUT.write_text(render_markdown(puzzle), encoding="utf-8")
    print(f"built knowledge puzzle markdown with {len(puzzle['nodes'])} nodes")


if __name__ == "__main__":
    main()
