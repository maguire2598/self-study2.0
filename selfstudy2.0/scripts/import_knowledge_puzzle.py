"""Import the approved knowledge-node array from a selector HTML file once."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "content" / "courses" / "collision-pi"
NODE_PATTERN = re.compile(
    r"\['([^']+)','([A-D])',([12]),'([^']*)','(核心|工具|选修|边界|拓展)','([^']*)'\]"
)
BOARD_TITLES = {
    "A": "碰撞现象与结论",
    "B": "现象与原理",
    "C": "几何化",
    "D": "从模型到π与位数关系",
}


def parse_nodes(source: Path) -> list[dict]:
    text = source.read_text(encoding="utf-8")
    nodes = [
        {
            "id": node_id,
            "board": board,
            "depth": int(depth),
            "title": title,
            "role": role,
            "summary": summary,
        }
        for node_id, board, depth, title, role, summary in NODE_PATTERN.findall(text)
    ]
    counts = Counter(node["board"] for node in nodes)
    expected = Counter({"A": 32, "B": 30, "C": 46, "D": 36})
    if len(nodes) != 144 or counts != expected:
        raise ValueError(f"unexpected node counts: total={len(nodes)}, boards={dict(counts)}")
    return nodes


def render_markdown(nodes: list[dict]) -> str:
    lines = [
        "# 碰撞与π知识拼图",
        "",
        "> 本目录由 `knowledge-puzzle.json` 生成；JSON 是节点单一真相来源。",
        "",
    ]
    for board, board_title in BOARD_TITLES.items():
        lines.extend([f"## [{board}] {board_title}", ""])
        for node in (item for item in nodes if item["board"] == board):
            indent = "  " if node["depth"] == 2 else ""
            role = f" · {node['role']}" if node["role"] != "核心" else ""
            lines.append(f"{indent}- **{node['id']} {node['title']}**{role}：{node['summary']}")
        lines.append("")
    lines.extend([
        "> C9 光线反射法为选修内容。",
        "",
        "> **文档版本**：1.0.0",
        "> **生成日期**：2026-08-19",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="approved selector HTML")
    args = parser.parse_args()
    nodes = parse_nodes(args.source)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    puzzle = {
        "$schema": "../../../schemas/knowledge_puzzle.schema.json",
        "course_id": "collision-pi",
        "version": "1.0.0",
        "nodes": nodes,
    }
    (OUTPUT_DIR / "knowledge-puzzle.json").write_text(
        json.dumps(puzzle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (OUTPUT_DIR / "knowledge-puzzle.md").write_text(render_markdown(nodes), encoding="utf-8")
    print("imported 144 nodes: A=32, B=30, C=46, D=36")


if __name__ == "__main__":
    main()
