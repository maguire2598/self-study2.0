"""Generate the formal Collision & Pi section B question bank."""

from __future__ import annotations

from pathlib import Path

if __package__:
    from .collision_pi_question_bank import build_bank_from_paths, write_bank
else:
    from collision_pi_question_bank import build_bank_from_paths, write_bank


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "courses" / "collision-pi" / "question-source-b.json"
PUZZLE = ROOT / "content" / "courses" / "collision-pi" / "knowledge-puzzle.json"
OUTPUT = ROOT / "content" / "courses" / "collision-pi" / "question-bank-b.json"


def build_bank() -> dict:
    return build_bank_from_paths(
        SOURCE,
        PUZZLE,
        section_id="B",
        title="碰撞与π · B板块客观题库",
    )


def main() -> None:
    bank = build_bank()
    write_bank(bank, OUTPUT)
    print(f"generated {len(bank['questions'])} questions -> {OUTPUT}")


if __name__ == "__main__":
    main()
