import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".txt", ".py", ".js", ".json", ".html", ".toml"}
EXEMPT = {
    ROOT / "docs" / "superpowers" / "specs" / "2026-08-18-selfstudy-2-clean-migration-design.md",
    ROOT / "docs" / "migration-report.md",
    Path(__file__).resolve(),
}
FORBIDDEN = [
    "C:\\Users\\MECHREVO\\selfstudy\\",
    ".codex\\visualizations",
    "web/scenario.json",
    "from backend",
    "import backend",
]


class IndependenceTests(unittest.TestCase):
    def test_runtime_and_config_files_do_not_depend_on_old_project(self):
        violations = []
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES or path in EXEMPT:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for forbidden in FORBIDDEN:
                if forbidden in text:
                    violations.append(f"{path.relative_to(ROOT)} contains {forbidden!r}")
        self.assertEqual(violations, [], "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
