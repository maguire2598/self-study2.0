"""Embed the generated question bank into the local authoring fragment."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "authoring" / "collision-pi-question-editor.template.html"
BANKS = {
    "A": ROOT / "content" / "courses" / "collision-pi" / "question-bank-a.json",
    "B": ROOT / "content" / "courses" / "collision-pi" / "question-bank-b.json",
}
STATE_HELPER = ROOT / "scripts" / "collision_pi_question_editor_state.js"
EDITOR = ROOT / "authoring" / "collision-pi-question-editor.html"


def build() -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    payload = {
        section: json.loads(path.read_text(encoding="utf-8"))
        for section, path in BANKS.items()
    }
    data = json.dumps(payload, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    state_helper = STATE_HELPER.read_text(encoding="utf-8")
    if "__QUESTION_BANKS_JSON__" not in template or "__QUESTION_EDITOR_STATE_JS__" not in template:
        raise ValueError("question editor placeholder is missing")
    return template.replace("__QUESTION_BANKS_JSON__", data).replace(
        "__QUESTION_EDITOR_STATE_JS__", state_helper
    )


def main() -> None:
    content = build()
    EDITOR.parent.mkdir(parents=True, exist_ok=True)
    EDITOR.write_text(content, encoding="utf-8")
    print(f"built editor with {content.count(chr(34) + 'assessment_kind' + chr(34))} questions")


if __name__ == "__main__":
    main()
