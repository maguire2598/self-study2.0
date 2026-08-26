"""Generate deterministic, safe SVG diagrams for Collision & Pi section C."""

from __future__ import annotations

import hashlib
import html
import json
import math
from pathlib import Path


VIEW_BOX = "0 0 640 420"
SVG_NS = "http://www.w3.org/2000/svg"
PLOT_RECT = (80, 45, 500, 315)
ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "content" / "courses" / "collision-pi" / "diagram-source-c.json"
OUTPUT_DIR = ROOT / "content" / "courses" / "collision-pi" / "diagrams" / "c"
MANIFEST_PATH = ROOT / "content" / "courses" / "collision-pi" / "diagram-manifest-c.json"

STYLE = """<style>
.frame{fill:#fffdf8;stroke:#cbd5e1;stroke-width:1}.axis{stroke:#64748b;stroke-width:1.5}.grid{stroke:#e2e8f0;stroke-width:1}.energy{fill:none;stroke:#0f766e;stroke-width:3}.momentum{fill:none;stroke:#c2410c;stroke-width:2.5}.state{fill:#2563eb;stroke:#fff;stroke-width:1.5}.state-chain{fill:none;stroke:#2563eb;stroke-width:2.5}.reflection{fill:none;stroke:#7c3aed;stroke-width:2.5}.sector{fill:#bbf7d0;fill-opacity:.65;stroke:#15803d;stroke-width:2}.wedge{fill:#fef3c7;fill-opacity:.65;stroke:#b45309;stroke-width:2}.ray{fill:none;stroke:#db2777;stroke-width:2.5}.arrow{stroke-linecap:round}.angle{fill:none;stroke:#b45309;stroke-width:2}.label{fill:#1e293b;font-family:Arial,'Microsoft YaHei',sans-serif;font-size:14px}.small-label{fill:#475569;font-family:Arial,'Microsoft YaHei',sans-serif;font-size:12px}.event-block{fill:#eff6ff;stroke:#2563eb;stroke-width:1}.event-wall{fill:#f5f3ff;stroke:#7c3aed;stroke-width:1}
</style>"""


def number(value: float) -> str:
    if abs(value) < 1e-12:
        value = 0.0
    return f"{value:.6f}".rstrip("0").rstrip(".")


def attrs(**values: object) -> str:
    return " ".join(
        f'{name.replace("_", "-")}="{html.escape(str(value), quote=True)}"'
        for name, value in values.items()
        if value is not None
    )


def element(name: str, content: str = "", **values: object) -> str:
    rendered = attrs(**values)
    return f"<{name} {rendered}>{content}</{name}>" if content else f"<{name} {rendered}/>"


def text(x: float, y: float, value: object, css_class: str = "label", anchor: str | None = None) -> str:
    return element(
        "text", html.escape(str(value)), x=number(x), y=number(y), **{"class": css_class, "text-anchor": anchor}
    )


def line(x1: float, y1: float, x2: float, y2: float, css_class: str, arrow: bool = False) -> str:
    return element(
        "line", x1=number(x1), y1=number(y1), x2=number(x2), y2=number(y2),
        **{"class": f"{css_class} arrow" if arrow else css_class, "marker-end": "url(#arrow-head)" if arrow else None},
    )


def dot(x: float, y: float, css_class: str = "state", radius: float = 5) -> str:
    return element("circle", cx=number(x), cy=number(y), r=number(radius), **{"class": css_class})


def path(commands: str, css_class: str) -> str:
    return element("path", d=commands, **{"class": css_class})


def plotter(points: list[tuple[float, float]], padding: float = 1.15):
    """Return a stable physical-coordinate transform within PLOT_RECT."""
    left, top, width, height = PLOT_RECT
    max_extent = max((max(abs(x), abs(y)) for x, y in points), default=1.0)
    extent = max(1.0, max_extent * padding)
    scale = min(width, height) / (2 * extent)
    cx, cy = left + width / 2, top + height / 2

    def project(x: float, y: float) -> tuple[float, float]:
        return cx + x * scale, cy - y * scale

    return project, scale, (cx, cy), extent


def axes(project, cx: float, cy: float, x_label: str, y_label: str) -> str:
    left, top, width, height = PLOT_RECT
    pieces = [
        element("rect", x=left, y=top, width=width, height=height, **{"class": "frame"}),
        line(left, cy, left + width, cy, "axis", True),
        line(cx, top + height, cx, top, "axis", True),
        text(left + width - 6, cy - 8, x_label, "small-label", "end"),
        text(cx + 8, top + 14, y_label, "small-label"),
    ]
    return "".join(pieces)


def circle_path(project, radius: float) -> str:
    cx, cy = project(0, 0)
    rx, _ = project(radius, 0)
    return element("circle", cx=number(cx), cy=number(cy), r=number(abs(rx - cx)), **{"class": "energy"})


def energy_radii(parameters: dict) -> tuple[float, float]:
    return (
        math.sqrt(2 * parameters["energy"] / parameters["mass_large"]),
        math.sqrt(2 * parameters["energy"] / parameters["mass_small"]),
    )


def svg_document(caption: str, alt_text: str, body: str) -> str:
    return (
        f'<svg xmlns="{SVG_NS}" viewBox="{VIEW_BOX}" role="img">'
        f"<title>{html.escape(caption)}</title><desc>{html.escape(alt_text)}</desc>"
        '<defs><marker id="arrow-head" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/></marker></defs>'
        f"{STYLE}{body}</svg>"
    )


def render_velocity_plane(diagram: dict) -> str:
    parameters, labels = diagram["parameters"], diagram["labels"]
    x_range, y_range = parameters["x_range"], parameters["y_range"]
    points = [(x_range[0], y_range[0]), (x_range[1], y_range[1])]
    project, _, (cx, cy), _ = plotter(points)
    body = axes(project, cx, cy, labels.get("x_axis", "vM"), labels.get("y_axis", "vm"))
    for index, state in enumerate(parameters["states"], 1):
        x, y = project(state["v_large"], state["v_small"])
        body += dot(x, y) + text(x + 9, y - 8, f"S{index}", "small-label")
    locations = [(540, 72), (120, 72), (120, 342), (540, 342)]
    for index, value in enumerate(parameters["quadrant_labels"].values()):
        x, y = locations[min(index, len(locations) - 1)]
        body += text(x, y, value, "small-label", "middle")
    return body


def render_energy_ellipse(diagram: dict) -> str:
    parameters, labels = diagram["parameters"], diagram["labels"]
    radius_x, radius_y = energy_radii(parameters)
    points = [(-radius_x, 0), (radius_x, 0), (0, -radius_y), (0, radius_y)]
    project, scale, (cx, cy), _ = plotter(points)
    body = axes(project, cx, cy, "vM", "vm")
    body += element("ellipse", cx=number(cx), cy=number(cy), rx=number(radius_x * scale), ry=number(radius_y * scale), **{"class": "energy"})
    for index, state in enumerate(parameters["states"], 1):
        x, y = project(state["v_large"], state["v_small"])
        body += dot(x, y) + text(x + 8, y - 8, f"S{index}", "small-label")
    if labels:
        body += text(330, 390, next(iter(labels.values())), "label", "middle")
    return body


def render_scale_pair(diagram: dict) -> str:
    parameters, labels = diagram["parameters"], diagram["labels"]
    raw_radius_x, raw_radius_y = energy_radii(parameters)
    weighted_radius = math.sqrt(2 * parameters["energy"])
    left_rect, right_rect = (35, 60, 265, 275), (340, 60, 265, 275)

    def panel_plot(rect, extent):
        left, top, width, height = rect
        scale = min(width, height) / (2 * max(1.0, extent * 1.18))
        cx, cy = left + width / 2, top + height / 2
        return lambda x, y: (cx + x * scale, cy - y * scale), scale, cx, cy

    raw_project, raw_scale, raw_cx, raw_cy = panel_plot(left_rect, max(raw_radius_x, raw_radius_y))
    weighted_project, weighted_scale, weighted_cx, weighted_cy = panel_plot(right_rect, weighted_radius)
    body = ""
    for rect, title_value in ((left_rect, labels.get("left", "速度坐标")), (right_rect, labels.get("right", "质量加权坐标"))):
        left, top, width, height = rect
        body += element("rect", x=left, y=top, width=width, height=height, **{"class": "frame"})
        body += text(left + width / 2, top - 10, title_value, "label", "middle")
    body += line(left_rect[0], raw_cy, left_rect[0] + left_rect[2], raw_cy, "axis", True)
    body += line(raw_cx, left_rect[1] + left_rect[3], raw_cx, left_rect[1], "axis", True)
    body += element("ellipse", cx=number(raw_cx), cy=number(raw_cy), rx=number(raw_radius_x * raw_scale), ry=number(raw_radius_y * raw_scale), **{"class": "energy"})
    body += line(right_rect[0], weighted_cy, right_rect[0] + right_rect[2], weighted_cy, "axis", True)
    body += line(weighted_cx, right_rect[1] + right_rect[3], weighted_cx, right_rect[1], "axis", True)
    body += element("circle", cx=number(weighted_cx), cy=number(weighted_cy), r=number(weighted_radius * weighted_scale), **{"class": "energy"})
    for index, (raw_state, weighted_state) in enumerate(zip(parameters["raw_states"], parameters["weighted_states"]), 1):
        raw_x, raw_y = raw_project(raw_state["v_large"], raw_state["v_small"])
        weighted_x, weighted_y = weighted_project(weighted_state["x"], weighted_state["y"])
        body += dot(raw_x, raw_y) + dot(weighted_x, weighted_y)
        body += text(raw_x + 7, raw_y - 7, f"S{index}", "small-label")
        body += text(weighted_x + 7, weighted_y - 7, f"S{index}", "small-label")
    return body


def render_momentum_chord(diagram: dict) -> str:
    parameters, labels = diagram["parameters"], diagram["labels"]
    radius = math.sqrt(2 * parameters["energy"])
    project, _, (cx, cy), _ = plotter([(-radius, -radius), (radius, radius)])
    body = axes(project, cx, cy, "x", "y") + circle_path(project, radius)
    normal_x, normal_y = math.sqrt(parameters["mass_large"]), math.sqrt(parameters["mass_small"])
    normal_size = normal_x * normal_x + normal_y * normal_y
    for momentum in parameters["momentum_values"]:
        distance = momentum / math.sqrt(normal_size)
        span = max(0.0, radius * radius - distance * distance) ** 0.5
        base_x, base_y = momentum * normal_x / normal_size, momentum * normal_y / normal_size
        unit_x, unit_y = normal_y / math.sqrt(normal_size), -normal_x / math.sqrt(normal_size)
        a, b = project(base_x + span * unit_x, base_y + span * unit_y), project(base_x - span * unit_x, base_y - span * unit_y)
        body += line(*a, *b, "momentum")
    for index, state in enumerate(parameters["intersections"], 1):
        x, y = project(state["x"], state["y"])
        body += dot(x, y) + text(x + 8, y - 8, f"S{index}", "small-label")
    if labels:
        body += text(330, 390, next(iter(labels.values())), "label", "middle")
    return body


def render_wall_reflection(diagram: dict) -> str:
    parameters, labels = diagram["parameters"], diagram["labels"]
    radius = math.sqrt(2 * parameters["energy"])
    project, _, (cx, cy), _ = plotter([(-radius, -radius), (radius, radius)])
    before, after = parameters["before"], parameters["after"]
    bx, by = project(before["x"], before["y"])
    ax, ay = project(after["x"], after["y"])
    body = axes(project, cx, cy, "x", "y") + circle_path(project, radius)
    body += line(bx, by, ax, ay, "reflection", True) + dot(bx, by) + dot(ax, ay)
    body += text(bx + 8, by - 8, "前", "small-label") + text(ax + 8, ay - 8, "后", "small-label")
    if labels:
        body += text(330, 390, next(iter(labels.values())), "label", "middle")
    return body


def render_state_chain(diagram: dict) -> str:
    parameters, labels = diagram["parameters"], diagram["labels"]
    states = parameters["states"]
    project, _, (cx, cy), _ = plotter([(state["x"], state["y"]) for state in states])
    body = axes(project, cx, cy, "x", "y")
    projected = [project(state["x"], state["y"]) for state in states]
    for index, ((x1, y1), (x2, y2), event) in enumerate(zip(projected, projected[1:], parameters["events"]), 1):
        css_class = "event-block" if event["kind"] == "block_collision" else "event-wall"
        body += line(x1, y1, x2, y2, "state-chain", True)
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        body += element("rect", x=number(mid_x - 34), y=number(mid_y - 22), width="68", height="18", rx="4", **{"class": css_class})
        body += text(mid_x, mid_y - 9, event["label"], "small-label", "middle")
    for index, (x, y) in enumerate(projected):
        body += dot(x, y) + text(x + 8, y + 18, f"S{index}", "small-label")
    if labels:
        body += text(330, 390, next(iter(labels.values())), "label", "middle")
    return body


def render_safe_sector(diagram: dict) -> str:
    parameters, labels = diagram["parameters"], diagram["labels"]
    radius = math.sqrt(2 * parameters["energy"])
    theta = math.atan(math.sqrt(parameters["mass_small"] / parameters["mass_large"]))
    project, _, (cx, cy), _ = plotter([(-radius, -radius), (radius, radius)])
    end_x, end_y = project(radius * math.cos(theta), radius * math.sin(theta))
    right_x, right_y = project(radius, 0)
    body = axes(project, cx, cy, "x", "y") + circle_path(project, radius)
    body += path(f"M {number(cx)} {number(cy)} L {number(right_x)} {number(right_y)} L {number(end_x)} {number(end_y)} Z", "sector")
    for state in parameters["boundary_states"]:
        x, y = project(state["x"], state["y"])
        body += dot(x, y)
    for index, value in enumerate(labels.values()):
        body += text(485, 82 + index * 20, value, "small-label", "middle")
    return body


def render_equal_angle(diagram: dict) -> str:
    parameters, labels = diagram["parameters"], diagram["labels"]
    radius = math.sqrt(2 * parameters["energy"])
    project, _, (cx, cy), _ = plotter([(-radius, -radius), (radius, radius)])
    states = parameters["states"]
    projected = [project(state["x"], state["y"]) for state in states]
    body = axes(project, cx, cy, "x", "y") + circle_path(project, radius)
    for (x1, y1), (x2, y2) in zip(projected, projected[1:]):
        body += line(x1, y1, x2, y2, "momentum")
    for index, (x, y) in enumerate(projected, 1):
        body += dot(x, y) + text(x + 8, y - 8, f"S{index}", "small-label")
    start_angle = math.atan2(states[0]["y"], states[0]["x"])
    end_angle = math.atan2(states[1]["y"], states[1]["x"])
    arc_radius = radius * 0.28
    sx, sy = project(arc_radius * math.cos(start_angle), arc_radius * math.sin(start_angle))
    ex, ey = project(arc_radius * math.cos(end_angle), arc_radius * math.sin(end_angle))
    body += path(f"M {number(sx)} {number(sy)} A {number(arc_radius * 15)} {number(arc_radius * 15)} 0 0 0 {number(ex)} {number(ey)}", "angle")
    if labels:
        body += text(330, 390, " · ".join(labels.values()), "label", "middle")
    return body


def render_element_legend(diagram: dict) -> str:
    parameters, labels = diagram["parameters"], diagram["labels"]
    radius = math.sqrt(2 * parameters["energy"])
    project, _, (cx, cy), _ = plotter([(-radius, -radius), (radius, radius)])
    state_a, state_b = parameters["states"][:2]
    a, b = project(state_a["x"], state_a["y"]), project(state_b["x"], state_b["y"])
    theta = math.atan(math.sqrt(parameters["mass_small"] / parameters["mass_large"]))
    sx, sy = project(radius, 0)
    ex, ey = project(radius * math.cos(theta), radius * math.sin(theta))
    body = axes(project, cx, cy, "x", "y") + circle_path(project, radius)
    body += path(f"M {number(cx)} {number(cy)} L {number(sx)} {number(sy)} L {number(ex)} {number(ey)} Z", "sector")
    body += line(*a, *b, "momentum") + line(a[0], a[1], a[0], 2 * cy - a[1], "reflection", True)
    body += dot(*a) + dot(*b)
    for index, value in enumerate(labels.values()):
        body += text(425, 70 + index * 22, value, "small-label")
    return body


def render_wedge_unfold(diagram: dict) -> str:
    parameters, labels = diagram["parameters"], diagram["labels"]
    crossings = parameters["crossings"]
    extent = max([4.0] + [abs(point["x"]) + abs(point["y"]) for point in crossings])
    project, _, (cx, cy), _ = plotter([(-extent, -extent), (extent, extent)])
    wedge_angle, ray_angle = parameters["wedge_angle"], parameters["ray_angle"]
    length = extent * 0.92
    origin = project(0, 0)
    upper = project(length * math.cos(wedge_angle), length * math.sin(wedge_angle))
    lower = project(length, 0)
    mirror = project(length * math.cos(-wedge_angle), length * math.sin(-wedge_angle))
    ray = project(length * math.cos(ray_angle), length * math.sin(ray_angle))
    body = axes(project, cx, cy, "X", "Y")
    body += path(f"M {number(origin[0])} {number(origin[1])} L {number(lower[0])} {number(lower[1])} L {number(upper[0])} {number(upper[1])} Z", "wedge")
    body += line(*origin, *upper, "wedge") + line(*origin, *mirror, "wedge") + line(*origin, *ray, "ray", True)
    for index, crossing in enumerate(crossings, 1):
        x, y = project(crossing["x"], crossing["y"])
        body += dot(x, y) + text(x + 8, y - 8, str(index), "small-label")
    if labels:
        body += text(330, 390, next(iter(labels.values())), "label", "middle")
    return body


RENDERERS = {
    "velocity_plane": render_velocity_plane,
    "energy_ellipse": render_energy_ellipse,
    "scale_pair": render_scale_pair,
    "momentum_chord": render_momentum_chord,
    "wall_reflection": render_wall_reflection,
    "state_chain": render_state_chain,
    "safe_sector": render_safe_sector,
    "equal_angle": render_equal_angle,
    "element_legend": render_element_legend,
    "wedge_unfold": render_wedge_unfold,
}


def render_diagram(diagram: dict) -> str:
    renderer = RENDERERS[diagram["template_kind"]]
    body = renderer(diagram)
    return svg_document(diagram["caption"], diagram["alt_text"], body)


def manifest_fingerprint(manifest: dict) -> str:
    canonical = {key: value for key, value in manifest.items() if key != "manifest_fingerprint"}
    payload = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_diagrams(source: dict) -> tuple[dict[str, str], dict]:
    rendered = {item["diagram_id"]: render_diagram(item) for item in source["diagrams"]}
    entries = []
    for item in source["diagrams"]:
        diagram_id = item["diagram_id"]
        payload = rendered[diagram_id].encode("utf-8")
        entries.append({
            "diagram_id": diagram_id,
            "path": f"content/courses/collision-pi/diagrams/c/{diagram_id}.svg",
            "width": 640,
            "height": 420,
            "template_kind": item["template_kind"],
            "coordinate_system": item["coordinate_system"],
            "caption": item["caption"],
            "alt_text": item["alt_text"],
            "sha256": hashlib.sha256(payload).hexdigest(),
        })
    manifest = {
        "course_id": "collision-pi",
        "section_id": "C",
        "version": source["version"],
        "diagrams": entries,
    }
    manifest["manifest_fingerprint"] = manifest_fingerprint(manifest)
    return rendered, manifest


def main() -> None:
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    svgs, manifest = build_diagrams(source)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for item in source["diagrams"]:
        diagram_id = item["diagram_id"]
        output_path = OUTPUT_DIR / f"{diagram_id}.svg"
        if output_path.name != f"{diagram_id}.svg" or output_path.stem != diagram_id:
            raise ValueError(f"unsafe output filename for {diagram_id!r}")
        output_path.write_text(svgs[diagram_id], encoding="utf-8", newline="\n")
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"generated {len(svgs)} diagrams -> {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
