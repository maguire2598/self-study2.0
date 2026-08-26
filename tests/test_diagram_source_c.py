import json
import math
import os
import re
import subprocess
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content/courses/collision-pi/diagram-source-c.json"
SCHEMA = ROOT / "schemas/collision_pi_diagram_source_c.schema.json"
PUZZLE = ROOT / "content/courses/collision-pi/knowledge-puzzle.json"

EXPECTED_TEMPLATE_COUNTS = Counter({
    "velocity_plane": 4,
    "energy_ellipse": 4,
    "scale_pair": 5,
    "momentum_chord": 5,
    "wall_reflection": 3,
    "state_chain": 5,
    "safe_sector": 3,
    "equal_angle": 3,
    "element_legend": 1,
    "wedge_unfold": 3,
})

EXPECTED_COORDINATE_COUNTS = Counter({
    "velocity_raw": 8,
    "velocity_weighted": 25,
    "position_weighted": 3,
})

EXPECTED_SOURCES = {
    "video-main": "sources/theory/弹性碰撞与π.txt",
    "openstax-ellipse": "https://openstax.org/books/precalculus-2e/pages/10-1-the-ellipse",
    "openstax-angles": "https://openstax.org/books/precalculus-2e/pages/5-1-angles",
    "openstax-unit-circle": "https://openstax.org/books/precalculus-2e/pages/5-2-unit-circle-sine-and-cosine-functions",
    "openstax-momentum": "https://openstax.org/books/physics/pages/8-2-conservation-of-momentum",
    "openstax-elastic": "https://openstax.org/books/college-physics/pages/8-4-elastic-collisions-in-one-dimension",
}

EXPECTED_DIAGRAM_IDS = (
    "cp-c-velocity-plane-quadrants", "cp-c-velocity-plane-initial",
    "cp-c-velocity-plane-terminal", "cp-c-velocity-plane-state-vs-path",
    "cp-c-energy-ellipse-equal-mass", "cp-c-energy-ellipse-ratio-4",
    "cp-c-energy-ellipse-ratio-16", "cp-c-energy-ellipse-same-energy",
    "cp-c-scale-pair-equal-mass", "cp-c-scale-pair-ratio-4",
    "cp-c-scale-pair-ratio-16", "cp-c-scale-pair-ratio-100",
    "cp-c-scale-pair-error-check", "cp-c-momentum-chord-ratio-1",
    "cp-c-momentum-chord-ratio-4", "cp-c-momentum-chord-ratio-16",
    "cp-c-momentum-chord-parallel", "cp-c-momentum-chord-intersections",
    "cp-c-wall-reflection-basic", "cp-c-wall-reflection-axis-check",
    "cp-c-wall-reflection-radius", "cp-c-state-chain-ratio-4",
    "cp-c-state-chain-ratio-9", "cp-c-state-chain-ratio-16",
    "cp-c-state-chain-ratio-100", "cp-c-state-chain-terminal",
    "cp-c-safe-sector-ratio-4", "cp-c-safe-sector-ratio-16",
    "cp-c-safe-sector-boundary", "cp-c-equal-angle-chord",
    "cp-c-equal-angle-step", "cp-c-equal-angle-count",
    "cp-c-element-legend-overview", "cp-c-wedge-unfold-basic",
    "cp-c-wedge-unfold-mirror", "cp-c-wedge-unfold-count",
)


def validate_source_with_pwsh(source):
    env = os.environ.copy()
    env["DIAGRAM_SOURCE_C_SCHEMA"] = str(SCHEMA)
    script = (
        "$json = [Console]::In.ReadToEnd(); "
        "try { "
        "$valid = $json | Test-Json -SchemaFile $env:DIAGRAM_SOURCE_C_SCHEMA -ErrorAction Stop; "
        "if ($valid) { exit 0 } else { exit 1 } "
        "} catch { [Console]::Error.WriteLine($_.Exception.Message); exit 1 }"
    )
    return subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", script],
        input=json.dumps(source, ensure_ascii=False),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


class DiagramSourceCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.diagrams = cls.source["diagrams"]
        cls.knowledge_node_ids = {
            node["id"] for node in json.loads(PUZZLE.read_text(encoding="utf-8"))["nodes"]
        }

    def assert_raw_energy_point(self, point, mass_large, mass_small, energy):
        actual = mass_large * point["v_large"] ** 2 + mass_small * point["v_small"] ** 2
        self.assertAlmostEqual(actual, 2 * energy)

    def assert_weighted_state(self, state, mass_large, mass_small):
        self.assertEqual(state["mass_large"], mass_large)
        self.assertEqual(state["mass_small"], mass_small)
        self.assertAlmostEqual(state["x"], mass_large ** 0.5 * state["v_large"])
        self.assertAlmostEqual(state["y"], mass_small ** 0.5 * state["v_small"])

    def assert_momentum_line(self, state, mass_large, mass_small, momentum):
        value = mass_large ** 0.5 * state["x"] + mass_small ** 0.5 * state["y"]
        self.assertAlmostEqual(value, momentum)

    def test_exact_diagram_contract(self):
        self.assertEqual(len(self.diagrams), 36)
        self.assertEqual(
            {source["id"]: source["location"] for source in self.source["source_catalog"]},
            EXPECTED_SOURCES,
        )
        ids = [diagram["diagram_id"] for diagram in self.diagrams]
        self.assertEqual(tuple(ids), EXPECTED_DIAGRAM_IDS)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(re.fullmatch(r"cp-c-[a-z0-9]+(?:-[a-z0-9]+)+", diagram_id) for diagram_id in ids))
        self.assertEqual(Counter(diagram["template_kind"] for diagram in self.diagrams), EXPECTED_TEMPLATE_COUNTS)
        self.assertEqual(Counter(diagram["coordinate_system"] for diagram in self.diagrams), EXPECTED_COORDINATE_COUNTS)
        for diagram in self.diagrams:
            with self.subTest(diagram=diagram["diagram_id"]):
                self.assertIn(diagram["node_id"], self.knowledge_node_ids)
                self.assertTrue(diagram["caption"].strip())
                self.assertTrue(diagram["alt_text"].strip())
                self.assertTrue(diagram["source_refs"])
                self.assertNotRegex(diagram["alt_text"], r"正确图|错误图|答案")

    def test_schema_accepts_the_contract_and_rejects_unknown_parameters(self):
        valid = validate_source_with_pwsh(self.source)
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        mutation = json.loads(json.dumps(self.source, ensure_ascii=False))
        mutation["diagrams"][0]["parameters"]["unexpected"] = "not a renderer input"
        invalid = validate_source_with_pwsh(mutation)
        self.assertNotEqual(invalid.returncode, 0, invalid.stdout + invalid.stderr)
        mutation = json.loads(json.dumps(self.source, ensure_ascii=False))
        mutation["diagrams"][0]["node_id"] = "C9.9"
        invalid = validate_source_with_pwsh(mutation)
        self.assertNotEqual(invalid.returncode, 0, invalid.stdout + invalid.stderr)

    def test_energy_ellipse_and_scale_pair_points_preserve_energy(self):
        for diagram in self.diagrams:
            parameters = diagram["parameters"]
            if diagram["template_kind"] == "energy_ellipse":
                for state in parameters["states"]:
                    self.assert_raw_energy_point(
                        state, parameters["mass_large"], parameters["mass_small"], parameters["energy"]
                    )
            elif diagram["template_kind"] == "scale_pair":
                for state in parameters["raw_states"]:
                    self.assert_raw_energy_point(
                        state, parameters["mass_large"], parameters["mass_small"], parameters["energy"]
                    )
                self.assertEqual(len(parameters["raw_states"]), len(parameters["weighted_states"]))
                for raw_state, state in zip(parameters["raw_states"], parameters["weighted_states"]):
                    self.assertEqual(state["v_large"], raw_state["v_large"])
                    self.assertEqual(state["v_small"], raw_state["v_small"])
                    self.assert_weighted_state(state, parameters["mass_large"], parameters["mass_small"])
                    self.assertAlmostEqual(state["x"] ** 2 + state["y"] ** 2, 2 * parameters["energy"])

    def test_weighted_state_templates_obey_coordinate_and_momentum_contracts(self):
        for diagram in self.diagrams:
            parameters = diagram["parameters"]
            kind = diagram["template_kind"]
            if kind == "momentum_chord":
                for intersection in parameters["intersections"]:
                    self.assert_weighted_state(
                        intersection, parameters["mass_large"], parameters["mass_small"]
                    )
                    self.assertAlmostEqual(intersection["x"] ** 2 + intersection["y"] ** 2, 2 * parameters["energy"])
                    self.assert_momentum_line(
                        intersection,
                        parameters["mass_large"],
                        parameters["mass_small"],
                        intersection["momentum"],
                    )
                    self.assertIn(intersection["momentum"], parameters["momentum_values"])
            elif kind in {"state_chain", "equal_angle", "element_legend"}:
                for state in parameters["states"]:
                    self.assert_weighted_state(state, parameters["mass_large"], parameters["mass_small"])

    def test_wall_reflections_preserve_x_and_reverse_y(self):
        for diagram in self.diagrams:
            if diagram["template_kind"] != "wall_reflection":
                continue
            before = diagram["parameters"]["before"]
            after = diagram["parameters"]["after"]
            parameters = diagram["parameters"]
            self.assert_weighted_state(before, parameters["mass_large"], parameters["mass_small"])
            self.assert_weighted_state(after, parameters["mass_large"], parameters["mass_small"])
            self.assertAlmostEqual(after["x"], before["x"])
            self.assertAlmostEqual(after["y"], -before["y"])

    def test_safe_sectors_are_within_the_terminal_wedge(self):
        for diagram in self.diagrams:
            if diagram["template_kind"] != "safe_sector":
                continue
            parameters = diagram["parameters"]
            slope = math.sqrt(parameters["mass_small"] / parameters["mass_large"])
            for state in parameters["boundary_states"]:
                self.assert_weighted_state(state, parameters["mass_large"], parameters["mass_small"])
                self.assertGreaterEqual(state["x"], 0)
                self.assertGreaterEqual(state["y"], 0)
                self.assertLessEqual(state["y"], slope * state["x"])

    def test_equal_angle_steps_match_mass_ratio(self):
        for diagram in self.diagrams:
            if diagram["template_kind"] != "equal_angle":
                continue
            parameters = diagram["parameters"]
            theta = math.atan(math.sqrt(parameters["mass_small"] / parameters["mass_large"]))
            self.assertAlmostEqual(parameters["theta"], theta)
            angles = [math.atan2(state["y"], state["x"]) for state in parameters["states"]]
            for before, after in zip(angles, angles[1:]):
                self.assertAlmostEqual(after - before, 2 * theta)

    def test_wedge_angles_match_mass_ratio(self):
        for diagram in self.diagrams:
            if diagram["template_kind"] != "wedge_unfold":
                continue
            parameters = diagram["parameters"]
            expected = math.atan(math.sqrt(parameters["mass_small"] / parameters["mass_large"]))
            self.assertAlmostEqual(parameters["wedge_angle"], expected)

    def test_state_chain_events_are_physical_transitions_with_conserved_energy(self):
        for diagram in self.diagrams:
            if diagram["template_kind"] != "state_chain":
                continue
            parameters = diagram["parameters"]
            states = parameters["states"]
            events = parameters["events"]
            mass_large = parameters["mass_large"]
            mass_small = parameters["mass_small"]
            self.assertEqual(len(events), len(states) - 1, diagram["diagram_id"])
            self.assertEqual(
                parameters["initial_velocity"],
                {"v_large": states[0]["v_large"], "v_small": states[0]["v_small"]},
                diagram["diagram_id"],
            )
            initial_energy_twice = (
                mass_large * states[0]["v_large"] ** 2
                + mass_small * states[0]["v_small"] ** 2
            )
            for state in states:
                self.assert_weighted_state(state, mass_large, mass_small)
                self.assertAlmostEqual(
                    mass_large * state["v_large"] ** 2 + mass_small * state["v_small"] ** 2,
                    initial_energy_twice,
                    msg=diagram["diagram_id"],
                )
            for before, event, after in zip(states, events, states[1:]):
                self.assertIsInstance(event, dict, diagram["diagram_id"])
                self.assertIn(event.get("kind"), {"block_collision", "wall_reflection"}, diagram["diagram_id"])
                self.assertTrue(event.get("label", "").strip(), diagram["diagram_id"])
                if event["kind"] == "block_collision":
                    denominator = mass_large + mass_small
                    self.assertAlmostEqual(
                        after["v_large"],
                        ((mass_large - mass_small) * before["v_large"] + 2 * mass_small * before["v_small"]) / denominator,
                    )
                    self.assertAlmostEqual(
                        after["v_small"],
                        (2 * mass_large * before["v_large"] + (mass_small - mass_large) * before["v_small"]) / denominator,
                    )
                else:
                    self.assertAlmostEqual(after["v_large"], before["v_large"])
                    self.assertAlmostEqual(after["v_small"], -before["v_small"])
            if diagram["diagram_id"] == "cp-c-state-chain-terminal":
                self.assertGreaterEqual(states[-1]["v_large"], states[-1]["v_small"])
                self.assertGreaterEqual(states[-1]["v_small"], 0)


if __name__ == "__main__":
    unittest.main()
