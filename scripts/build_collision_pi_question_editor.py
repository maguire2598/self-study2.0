"""Embed the generated question bank into the local authoring fragment."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "authoring" / "collision-pi-question-editor.template.html"
BANK = ROOT / "content" / "courses" / "collision-pi" / "question-bank-a.json"
EDITOR = ROOT / "authoring" / "collision-pi-question-editor.html"


def build() -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    bank = BANK.read_text(encoding="utf-8").strip()
    if "__QUESTION_BANK_JSON__" not in template:
        raise ValueError("question bank placeholder is missing")
    return template.replace("__QUESTION_BANK_JSON__", bank)


def main() -> None:
    content = build()
    EDITOR.parent.mkdir(parents=True, exist_ok=True)
    EDITOR.write_text(content, encoding="utf-8")
    print(f"built editor with {content.count(chr(34) + 'assessment_kind' + chr(34))} questions")


if __name__ == "__main__":
    main()
