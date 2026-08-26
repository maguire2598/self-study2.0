import hashlib
import json
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.generate_collision_pi_c_diagrams import (
    build_diagrams,
    manifest_fingerprint,
    render_diagram,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "content" / "courses" / "collision-pi" / "diagram-source-c.json"
OUTPUT_DIR = ROOT / "content" / "courses" / "collision-pi" / "diagrams" / "c"
MANIFEST_PATH = ROOT / "content" / "courses" / "collision-pi" / "diagram-manifest-c.json"
SVG_NS = "{http://www.w3.org/2000/svg}"


class CollisionPiCDiagramTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    def test_builds_complete_accessible_safe_diagram_set(self):
        """Removing SVG accessibility or safety handling must fail this contract."""
        svgs, manifest = build_diagrams(self.source)

        self.assertEqual(len(svgs), 36)
        self.assertEqual(len(manifest["diagrams"]), 36)
        self.assertRegex(manifest["manifest_fingerprint"], r"^[0-9a-f]{64}$")
        self.assertEqual(manifest["manifest_fingerprint"], manifest_fingerprint(manifest))

        for diagram_id, svg in svgs.items():
            with self.subTest(diagram_id=diagram_id):
                root = ET.fromstring(svg)
                self.assertEqual(root.tag, SVG_NS + "svg")
                self.assertEqual(root.attrib.get("viewBox"), "0 0 640 420")
                self.assertIsNotNone(root.find(SVG_NS + "title"))
                self.assertIsNotNone(root.find(SVG_NS + "desc"))
                self.assertNotIn("<script", svg.lower())
                self.assertNotIn("foreignobject", svg.lower())
                self.assertNotRegex(svg, r"(?:href|src)\s*=\s*[\"'][^\"']*(?:https?:|//)", re.I)
                for element in root.iter():
                    self.assertNotEqual(element.tag, SVG_NS + "script")
                    self.assertNotEqual(element.tag, SVG_NS + "foreignObject")
                    for name, value in element.attrib.items():
                        self.assertFalse(name.lower().startswith("on"), (name, value))
                        if name.lower().endswith("href") or name.lower() == "src":
                            self.assertNotRegex(value, r"^(?:https?:|//)")

    def test_render_escapes_source_text_without_interpreting_markup(self):
        """Removing html.escape from SVG text must fail this rendering boundary."""
        diagram = json.loads(json.dumps(self.source["diagrams"][0], ensure_ascii=False))
        diagram["caption"] = "标题 <b>不是元素</b> & 保留"
        diagram["alt_text"] = "说明 <img src=x> & 安全"
        diagram["parameters"]["quadrant_labels"]["I"] = "<em>标签</em> & 文本"

        svg = render_diagram(diagram)
        root = ET.fromstring(svg)
        self.assertEqual(root.findtext(SVG_NS + "title"), diagram["caption"])
        self.assertEqual(root.findtext(SVG_NS + "desc"), diagram["alt_text"])
        self.assertIn("&lt;b&gt;不是元素&lt;/b&gt; &amp; 保留", svg)
        self.assertIn("&lt;em&gt;标签&lt;/em&gt; &amp; 文本", svg)
        self.assertNotIn("<b>", svg)
        self.assertNotIn("<em>", svg)

    def test_generated_files_match_manifest_exactly(self):
        """Omitting, renaming, or changing a generated diagram must fail publication checks."""
        subprocess.run(
            [sys.executable, "scripts/generate_collision_pi_c_diagrams.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        expected_ids = [diagram["diagram_id"] for diagram in self.source["diagrams"]]
        self.assertEqual([entry["diagram_id"] for entry in manifest["diagrams"]], expected_ids)
        self.assertEqual({path.stem for path in OUTPUT_DIR.glob("*.svg")}, set(expected_ids))
        self.assertEqual(manifest["manifest_fingerprint"], manifest_fingerprint(manifest))

        for entry in manifest["diagrams"]:
            with self.subTest(diagram_id=entry["diagram_id"]):
                path = ROOT / entry["path"]
                self.assertTrue(path.is_file())
                payload = path.read_bytes()
                self.assertEqual(entry["width"], 640)
                self.assertEqual(entry["height"], 420)
                self.assertEqual(entry["sha256"], hashlib.sha256(payload).hexdigest())
                ET.fromstring(payload)

    def test_build_is_deterministic(self):
        """Using unordered output or unstable formatting must fail determinism checks."""
        first_svgs, first_manifest = build_diagrams(self.source)
        second_svgs, second_manifest = build_diagrams(self.source)
        self.assertEqual(first_svgs, second_svgs)
        self.assertEqual(first_manifest, second_manifest)

    def test_geometry_uses_stable_semantic_css_classes(self):
        """Collapsing geometry semantics into unclassified SVG elements must fail."""
        svgs, _ = build_diagrams(self.source)
        expected_classes = {
            "cp-c-velocity-plane-quadrants": {"axis", "state"},
            "cp-c-energy-ellipse-ratio-4": {"axis", "energy", "state"},
            "cp-c-momentum-chord-ratio-4": {"axis", "energy", "momentum", "state"},
            "cp-c-wall-reflection-basic": {"axis", "energy", "reflection", "arrow", "state"},
            "cp-c-equal-angle-step": {"axis", "energy", "momentum", "angle", "state"},
            "cp-c-safe-sector-ratio-4": {"axis", "energy", "sector", "state"},
        }
        for diagram_id, required in expected_classes.items():
            with self.subTest(diagram_id=diagram_id):
                root = ET.fromstring(svgs[diagram_id])
                actual = {
                    css_class
                    for element in root.iter()
                    for css_class in element.attrib.get("class", "").split()
                }
                self.assertTrue(required <= actual, (required, actual))

    def test_unfolded_ray_contains_every_declared_crossing_marker(self):
        """Plotting folded crossings away from the authoritative unfolded ray must fail."""
        svgs, _ = build_diagrams(self.source)
        for diagram in self.source["diagrams"]:
            if diagram["template_kind"] != "wedge_unfold":
                continue
            with self.subTest(diagram_id=diagram["diagram_id"]):
                root = ET.fromstring(svgs[diagram["diagram_id"]])
                ray = next(
                    element for element in root.iter()
                    if "ray" in element.attrib.get("class", "").split()
                )
                markers = [
                    element for element in root.iter()
                    if "crossing" in element.attrib.get("class", "").split()
                ]
                self.assertEqual(len(markers), len(diagram["parameters"]["crossings"]))
                x1, y1 = float(ray.attrib["x1"]), float(ray.attrib["y1"])
                dx = float(ray.attrib["x2"]) - x1
                dy = float(ray.attrib["y2"]) - y1
                length_squared = dx * dx + dy * dy
                positions = []
                for marker in markers:
                    mx, my = float(marker.attrib["cx"]), float(marker.attrib["cy"])
                    distance_from_ray = abs((mx - x1) * dy - (my - y1) * dx) / length_squared ** 0.5
                    self.assertLessEqual(distance_from_ray, 0.0001)
                    positions.append(((mx - x1) * dx + (my - y1) * dy) / length_squared)
                self.assertTrue(all(0.0 <= position <= 1.0 for position in positions))
                self.assertEqual(positions, sorted(positions))

    def test_each_equal_angle_interval_has_an_arc_and_marker_label(self):
        """Rendering only the first equal-angle interval must fail this comparison contract."""
        svgs, _ = build_diagrams(self.source)
        for diagram in self.source["diagrams"]:
            if diagram["template_kind"] != "equal_angle":
                continue
            with self.subTest(diagram_id=diagram["diagram_id"]):
                root = ET.fromstring(svgs[diagram["diagram_id"]])
                interval_count = len(diagram["parameters"]["states"]) - 1
                angle_arcs = [
                    element for element in root.iter()
                    if "angle" in element.attrib.get("class", "").split()
                ]
                angle_labels = [
                    element for element in root.iter()
                    if "angle-label" in element.attrib.get("class", "").split()
                ]
                self.assertEqual(len(angle_arcs), interval_count)
                self.assertEqual(len(angle_labels), interval_count)
                self.assertTrue(all(element.text == diagram["labels"].get("step", "2θ") for element in angle_labels))


if __name__ == "__main__":
    unittest.main()
