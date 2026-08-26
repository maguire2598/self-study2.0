# Collision & Pi C Visual Question Bank Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 生成 C 板块 180 道客观题、36 个确定性 SVG 图像实例，并把 A/B 作者筛选器扩展为支持 C 板块图文题的作者工具。

**Architecture:** 保持 `knowledge-puzzle.json` 中现有 46 个 C 节点和全部 `node_id` 不变。新增声明式图像源，经纯 Python 模板生成 SVG 与 manifest；C 题源只引用稳定的 `diagram_id`，共享题库生成器将图像元数据透传到正式 C bank，并把 manifest 指纹纳入 bank 内容指纹；作者工具嵌入 A/B/C 三个 bank 和 C 图像 manifest。

**Tech Stack:** Python 3.13 标准库、JSON Schema Draft 2020-12、SVG 1.1、HTML/CSS/原生 JavaScript、Node.js 静态验证、Python `unittest`、本地 UTF-8 HTTP 服务、应用内浏览器。

**Spec:** `docs/superpowers/specs/2026-08-26-collision-pi-c-visual-question-bank-design.md`

## Global Constraints

- C 保持 9 个一级节点、37 个承载题目的二级节点和 46 个节点总量，不迁移任何 `node_id`。
- C bank 恰有 180 道客观题，其中 C1-C8 为 168 道核心题，C9 为 12 道选修题。
- 风格分布固定为 `scenario=108`、`calculation=24`、`concise=48`。
- 呈现分布固定为 `text_only=60`、`stem_figure=72`、`option_figures=24`、`figure_sequence=24`，共 120 道配图题。
- 图像资产固定为 10 类模板和 36 个 SVG 实例，只由声明式 JSON 和仓库模板生成。
- 坐标体系只允许 `velocity_raw`、`velocity_weighted`、`position_weighted`；每张图必须显式声明。
- A bank 保持 140 题和原字节不变，B bank 保持 168 题和原字节不变。
- 状态观察题不生成；标准答案和解析只用于作者端与判题端；学生答错后不直接显示答案或解析。
- AI 不把单次答题结果解释为心理诊断，知识学习模块必须能独立运行。
- 正式图像全部原创生成，不复制 OpenStax、视频或其他教材图片。
- 不实现自由绘图判分、拖拽作图、Canvas 交互、动画或学生运行时。
- 所有 JSON、SVG、bank 和作者 HTML 连续构建两遍后必须字节一致。

---

## File Structure

### 声明式图像模型

- Create: `content/courses/collision-pi/diagram-source-c.json` - 36 个图像实例的唯一作者源。
- Create: `schemas/collision_pi_diagram_source_c.schema.json` - 锁定模板、坐标、参数分支、ID 和实例数量。
- Create: `tests/test_diagram_source_c.py` - 独立复算坐标、能量、动量、反射、角度和楔形关系。

### SVG 与 manifest 生成

- Create: `scripts/generate_collision_pi_c_diagrams.py` - 纯函数渲染器、SHA-256 与确定性写出。
- Create: `content/courses/collision-pi/diagrams/c/*.svg` - 36 个生成资产。
- Create: `content/courses/collision-pi/diagram-manifest-c.json` - 图像路径、尺寸、无障碍文字、坐标和指纹。
- Create: `tests/test_collision_pi_c_diagrams.py` - 生成一致性、SVG 安全性和 manifest 合同。

### C 题源与正式 bank

- Create: `content/courses/collision-pi/question-source-c.json` - 12 个场景题组、24 个计算夹具和 180 道作者题。
- Create: `schemas/objective_question_source_c.schema.json` - 锁定 C 题源和四种图像呈现方式。
- Create: `tests/test_question_source_c.py` - 配额、物理复算、图文引用和文案质量。
- Modify: `scripts/collision_pi_question_bank.py` - 可选图像字段透传、图像引用校验和 manifest 指纹。
- Create: `scripts/generate_collision_pi_c_questions.py` - C 的薄入口。
- Create: `content/courses/collision-pi/question-bank-c.json` - 180 道正式 C 题。
- Modify: `schemas/objective_question_bank.schema.json` - 新增 C 条件分支，不改变 A/B 合同。
- Create: `tests/test_question_bank_c.py` - 正式 C bank、选项轮换和 A/B 无漂移验证。

### A/B/C 作者工具

- Modify: `scripts/build_collision_pi_question_editor.py` - 嵌入 C bank 和图像 manifest。
- Modify: `scripts/collision_pi_question_editor_state.js` - C 草稿和图像指纹匹配。
- Modify: `authoring/collision-pi-question-editor.template.html` - C 筛选器、图片、图片选项和序列渲染。
- Modify: `authoring/collision-pi-question-editor.html` - 确定性生成结果。
- Modify: `scripts/validate_question_editor.js` - A/B/C 数据、图像和控件静态检查。
- Modify: `scripts/validate_question_editor_state.js` - 三板块草稿隔离和过期图像拒绝。
- Modify: `tests/test_project_contract.py` - 生成一致性和三板块当前合同。

### 当前项目事实

- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/roadmap.md`
- Modify: `docs/decisions/conversation-decisions.md`

---

### Task 1: 建立 36 个声明式图像实例和物理合同

**Files:**
- Create: `content/courses/collision-pi/diagram-source-c.json`
- Create: `schemas/collision_pi_diagram_source_c.schema.json`
- Create: `tests/test_diagram_source_c.py`

**Interfaces:**
- Consumes: `knowledge-puzzle.json` 中的 C1-C9 节点、规格中的 10 类模板与 3 个坐标体系、课程主来源和五个 OpenStax 核对来源。
- Produces: 通过严格 Schema 和独立物理复算的 36 项 JSON 数据；后续渲染器只依赖 `diagram_id`、`template_kind`、`coordinate_system`、`parameters`、`labels`、`caption`、`alt_text`、`source_refs`。

- [ ] **Step 1: 写图像源失败测试**

创建 `tests/test_diagram_source_c.py`，先锁定下列常量：

```python
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
```

测试必须断言：共 36 项、ID 唯一、模板和坐标计数精确、`caption` 与 `alt_text` 非空、每项至少一个 `source_ref`、`alt_text` 不含“正确图”“错误图”“答案”，且图像 ID 匹配 `^cp-c-[a-z0-9]+(?:-[a-z0-9]+)+$`。

- [ ] **Step 2: 添加独立物理复算测试**

测试不要读取题目答案或解析作为预期值。对各模板按参数复算：

```python
def assert_raw_energy_point(self, point, mass_large, mass_small, energy):
    actual = mass_large * point["v_large"] ** 2 + mass_small * point["v_small"] ** 2
    self.assertAlmostEqual(actual, 2 * energy)

def assert_weighted_state(self, state):
    self.assertAlmostEqual(state["x"], state["mass_large"] ** 0.5 * state["v_large"])
    self.assertAlmostEqual(state["y"], state["mass_small"] ** 0.5 * state["v_small"])

def assert_momentum_line(self, state, mass_large, mass_small, momentum):
    value = mass_large ** 0.5 * state["x"] + mass_small ** 0.5 * state["y"]
    self.assertAlmostEqual(value, momentum)
```

另行检查：墙反射满足 `x_after=x_before`、`y_after=-y_before`；安全区域满足 `x>=0`、`0<=y<=sqrt(m/M)*x`；等角图满足 `theta=atan(sqrt(m/M))` 和相邻状态角差 `2*theta`；楔形图满足楔形角 `atan(sqrt(m/M))`。

- [ ] **Step 3: 运行测试并确认 RED**

Run:

```powershell
python -m unittest tests.test_diagram_source_c -v
```

Expected: 因 `diagram-source-c.json` 和 Schema 尚不存在而失败；现有 A/B 测试不受影响。

- [ ] **Step 4: 编写严格图像源 Schema**

创建 Draft 2020-12 Schema，根对象使用 `additionalProperties: false`，并要求：

```json
{
  "required": ["course_id", "section_id", "version", "source_catalog", "diagrams"],
  "properties": {
    "course_id": {"const": "collision-pi"},
    "section_id": {"const": "C"},
    "version": {"const": "1.0.0"},
    "diagrams": {"type": "array", "minItems": 36, "maxItems": 36}
  }
}
```

图像项按 `template_kind` 使用 `if/then` 或 `oneOf` 路由，参数键固定如下：

| 模板 | `coordinate_system` | 必填参数 |
| --- | --- | --- |
| `velocity_plane` | `velocity_raw` | `x_range`、`y_range`、`states`、`quadrant_labels` |
| `energy_ellipse` | `velocity_raw` | `mass_large`、`mass_small`、`energy`、`states` |
| `scale_pair` | `velocity_weighted` | `mass_large`、`mass_small`、`energy`、`raw_states`、`weighted_states`、`source_coordinate_system=velocity_raw` |
| `momentum_chord` | `velocity_weighted` | `mass_large`、`mass_small`、`energy`、`momentum_values`、`intersections` |
| `wall_reflection` | `velocity_weighted` | `mass_large`、`mass_small`、`energy`、`before`、`after` |
| `state_chain` | `velocity_weighted` | `mass_large`、`mass_small`、`initial_velocity`、`states`、`events` |
| `safe_sector` | `velocity_weighted` | `mass_large`、`mass_small`、`energy`、`boundary_states` |
| `equal_angle` | `velocity_weighted` | `mass_large`、`mass_small`、`energy`、`theta`、`states` |
| `element_legend` | `velocity_weighted` | `mass_large`、`mass_small`、`energy`、`momentum`、`states` |
| `wedge_unfold` | `position_weighted` | `mass_large`、`mass_small`、`wedge_angle`、`ray_angle`、`crossings` |

`scale_pair` 的主坐标体系声明为 `velocity_weighted`，但左右子图必须分别标明 `velocity_raw` 和 `velocity_weighted`，避免把两个子图的 `x/y` 含义混用。

- [ ] **Step 5: 编写来源目录和 36 个实例**

来源 ID 固定为：

```text
video-main
openstax-ellipse
openstax-angles
openstax-unit-circle
openstax-momentum
openstax-elastic
```

来源地址固定为：

```text
video-main -> sources/theory/弹性碰撞与π.txt
openstax-ellipse -> https://openstax.org/books/precalculus-2e/pages/10-1-the-ellipse
openstax-angles -> https://openstax.org/books/precalculus-2e/pages/5-1-angles
openstax-unit-circle -> https://openstax.org/books/precalculus-2e/pages/5-2-unit-circle-sine-and-cosine-functions
openstax-momentum -> https://openstax.org/books/physics/pages/8-2-conservation-of-momentum
openstax-elastic -> https://openstax.org/books/college-physics/pages/8-4-elastic-collisions-in-one-dimension
```

36 个图像 ID 固定为：

```text
cp-c-velocity-plane-quadrants
cp-c-velocity-plane-initial
cp-c-velocity-plane-terminal
cp-c-velocity-plane-state-vs-path
cp-c-energy-ellipse-equal-mass
cp-c-energy-ellipse-ratio-4
cp-c-energy-ellipse-ratio-16
cp-c-energy-ellipse-same-energy
cp-c-scale-pair-equal-mass
cp-c-scale-pair-ratio-4
cp-c-scale-pair-ratio-16
cp-c-scale-pair-ratio-100
cp-c-scale-pair-error-check
cp-c-momentum-chord-ratio-1
cp-c-momentum-chord-ratio-4
cp-c-momentum-chord-ratio-16
cp-c-momentum-chord-parallel
cp-c-momentum-chord-intersections
cp-c-wall-reflection-basic
cp-c-wall-reflection-axis-check
cp-c-wall-reflection-radius
cp-c-state-chain-ratio-4
cp-c-state-chain-ratio-9
cp-c-state-chain-ratio-16
cp-c-state-chain-ratio-100
cp-c-state-chain-terminal
cp-c-safe-sector-ratio-4
cp-c-safe-sector-ratio-16
cp-c-safe-sector-boundary
cp-c-equal-angle-chord
cp-c-equal-angle-step
cp-c-equal-angle-count
cp-c-element-legend-overview
cp-c-wedge-unfold-basic
cp-c-wedge-unfold-mirror
cp-c-wedge-unfold-count
```

使用小整数质量和能量，优先让点坐标为整数或简单根式。`states` 和 `intersections` 同时保存物理速度与绘图坐标，便于测试核对，不把像素坐标当成物理值。

- [ ] **Step 6: 运行 Schema 与物理测试**

Run:

```powershell
python -m unittest tests.test_diagram_source_c -v
$json = Get-Content -Raw content/courses/collision-pi/diagram-source-c.json
if (-not (Test-Json -Json $json -SchemaFile schemas/collision_pi_diagram_source_c.schema.json)) { throw 'C diagram source schema failed' }
```

Expected: 36 个实例、10 类模板、3 个坐标体系和全部物理复算通过。

- [ ] **Step 7: 提交声明式图像模型**

```powershell
git add content/courses/collision-pi/diagram-source-c.json schemas/collision_pi_diagram_source_c.schema.json tests/test_diagram_source_c.py
git commit -m "feat: model collision pi C diagrams"
```

---

### Task 2: 生成确定性 SVG 和图像 manifest

**Files:**
- Create: `scripts/generate_collision_pi_c_diagrams.py`
- Create: `content/courses/collision-pi/diagrams/c/*.svg`
- Create: `content/courses/collision-pi/diagram-manifest-c.json`
- Create: `tests/test_collision_pi_c_diagrams.py`

**Interfaces:**
- Consumes: Task 1 的 36 个声明式图像项。
- Produces: `build_diagrams(source: dict) -> tuple[dict[str, str], dict]`；字典键为 `diagram_id`，值为完整 SVG 字符串；manifest 供 C bank 和作者工具引用。

- [ ] **Step 1: 写失败的渲染与 manifest 测试**

创建 `tests/test_collision_pi_c_diagrams.py`，要求这些公共函数存在：

```python
from scripts.generate_collision_pi_c_diagrams import (
    build_diagrams,
    manifest_fingerprint,
    render_diagram,
)
```

测试必须检查：

```python
svgs, manifest = build_diagrams(source)
self.assertEqual(len(svgs), 36)
self.assertEqual(len(manifest["diagrams"]), 36)
self.assertRegex(manifest["manifest_fingerprint"], r"^[0-9a-f]{64}$")
self.assertEqual(manifest["manifest_fingerprint"], manifest_fingerprint(manifest))
```

逐个 SVG 用 `xml.etree.ElementTree.fromstring` 解析，要求统一 `viewBox="0 0 640 420"`、存在 `<title>` 和 `<desc>`、禁止 `<script>`、`foreignObject`、外部 URL、事件属性和未转义的任意 HTML。

- [ ] **Step 2: 运行测试并确认 RED**

```powershell
python -m unittest tests.test_collision_pi_c_diagrams -v
```

Expected: 生成模块和输出文件不存在。

- [ ] **Step 3: 实现确定性渲染公共层**

在 `generate_collision_pi_c_diagrams.py` 中定义：

```python
VIEW_BOX = "0 0 640 420"
SVG_NS = "http://www.w3.org/2000/svg"

def number(value: float) -> str:
    if abs(value) < 1e-12:
        value = 0.0
    return f"{value:.6f}".rstrip("0").rstrip(".")

def render_diagram(diagram: dict) -> str:
    renderer = RENDERERS[diagram["template_kind"]]
    body = renderer(diagram)
    return svg_document(diagram["caption"], diagram["alt_text"], body)

def manifest_fingerprint(manifest: dict) -> str:
    canonical = {k: v for k, v in manifest.items() if k != "manifest_fingerprint"}
    payload = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
```

只使用标准库 `html.escape` 处理文字。颜色、线型、点形、箭头和标签由固定常量定义；不得从 JSON 接收 SVG、CSS、HTML 或 JavaScript 片段。

- [ ] **Step 4: 实现 10 个模板渲染器**

`RENDERERS` 的键必须与 Task 1 完全一致：

```python
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
```

使用纯函数把物理坐标映射到 `plot_rect=(80, 45, 500, 315)`。坐标轴、能量曲线、动量线、点、箭头、角弧和安全区域分别使用稳定的 CSS class。每个模板只计算其负责的几何元素，不在题源中保存像素路径。

- [ ] **Step 5: 写出 SVG 和 manifest**

实现：

```python
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
    manifest = {"course_id": "collision-pi", "section_id": "C", "version": source["version"], "diagrams": entries}
    manifest["manifest_fingerprint"] = manifest_fingerprint(manifest)
    return rendered, manifest
```

`main()` 按 source 数组顺序写文件，先检查输出文件名与 `diagram_id` 一致，再写 `diagram-manifest-c.json`。不要清理未识别目录；测试通过精确文件集合发现多余 SVG。

- [ ] **Step 6: 运行两轮生成和哈希验证**

```powershell
python scripts/generate_collision_pi_c_diagrams.py
$first = Get-FileHash content/courses/collision-pi/diagram-manifest-c.json -Algorithm SHA256
python scripts/generate_collision_pi_c_diagrams.py
$second = Get-FileHash content/courses/collision-pi/diagram-manifest-c.json -Algorithm SHA256
if ($first.Hash -ne $second.Hash) { throw 'diagram manifest is not deterministic' }
python -m unittest tests.test_diagram_source_c tests.test_collision_pi_c_diagrams -v
```

Expected: 两轮 manifest 哈希一致，36 个 SVG 的单图哈希与 manifest 一致。

- [ ] **Step 7: 提交生成器和资产**

```powershell
git add scripts/generate_collision_pi_c_diagrams.py content/courses/collision-pi/diagrams/c content/courses/collision-pi/diagram-manifest-c.json tests/test_collision_pi_c_diagrams.py
git commit -m "feat: generate collision pi C SVG diagrams"
```

---

### Task 3: 编写严格的 180 道 C 题源

**Files:**
- Create: `content/courses/collision-pi/question-source-c.json`
- Create: `schemas/objective_question_source_c.schema.json`
- Create: `tests/test_question_source_c.py`

**Interfaces:**
- Consumes: 37 个 C 二级节点、36 项 diagram manifest、6 个来源 ID 和 Task 1 的物理参数。
- Produces: 单一可审阅 C 题源，包含 12 个有序场景、108 道场景题、24 道计算题、48 道独立短题和精确图像引用。

- [ ] **Step 1: 写精确配额和场景失败测试**

在 `tests/test_question_source_c.py` 定义：

```python
EXPECTED_QUOTAS = {
    "C1.1": 6, "C1.2": 6, "C1.3": 5, "C1.4": 5,
    "C2.1": 6, "C2.2": 6, "C2.3": 6,
    "C3.1": 6, "C3.2": 6, "C3.3": 7, "C3.4": 4, "C3.5": 3,
    "C4.1": 6, "C4.2": 6, "C4.3": 6, "C4.4": 6,
    "C5.1": 6, "C5.2": 6, "C5.3": 6,
    "C6.1": 6, "C6.2": 6, "C6.3": 6, "C6.4": 6,
    "C7.1": 6, "C7.2": 6, "C7.3": 6, "C7.4": 6,
    "C8.1": 4, "C8.2": 4, "C8.3": 4,
    "C9.1": 1, "C9.2": 1, "C9.3": 2, "C9.4": 2,
    "C9.5": 2, "C9.6": 2, "C9.7": 2,
}

EXPECTED_SCENARIO_NODE_COUNTS = {
    "SC-C1-STATE": {"C1.1": 4, "C1.2": 4, "C1.3": 3, "C1.4": 3},
    "SC-C2-ELLIPSE": {"C2.1": 4, "C2.2": 4, "C2.3": 4},
    "SC-C3-SCALE": {"C3.1": 4, "C3.2": 4, "C3.3": 5, "C3.4": 2, "C3.5": 1},
    "SC-C4-CHORD": {"C4.1": 4, "C4.2": 4, "C4.3": 4, "C4.4": 4},
    "SC-C5-WALL": {"C5.1": 4, "C5.2": 4, "C5.3": 4},
    "SC-C6-CHAIN": {"C6.1": 3, "C6.2": 4, "C6.4": 3},
    "SC-C6-SAFE": {"C6.1": 1, "C6.2": 1, "C6.3": 5, "C6.4": 1},
    "SC-C7-ANGLE": {"C7.1": 3, "C7.2": 3, "C7.3": 2},
    "SC-C7-COUNT": {"C7.1": 1, "C7.2": 1, "C7.3": 2, "C7.4": 4},
    "SC-C8-LEGEND": {"C8.1": 1, "C8.2": 1},
    "SC-C9-WEDGE": {"C9.1": 1},
    "SC-C9-UNFOLD": {"C9.4": 1},
}
```

断言场景顺序与字典顺序完全一致，场景题总数为 108，独立题总数为 72，所有 `(node_id, key)` 唯一。

在同一测试类中定义 `test_c1_c3_checkpoint`、`test_c4_c6_checkpoint` 和 `test_c7_c9_checkpoint`。三个方法分别按节点前缀选取 66、66、48 道题，并复用配额、答案载荷、图像引用、夹具归属和文案守卫辅助函数。

- [ ] **Step 2: 锁定风格、题型和呈现分布**

```python
self.assertEqual(
    Counter(q["question_style"] for q in all_questions),
    Counter({"scenario": 108, "calculation": 24, "concise": 48}),
)
self.assertEqual(
    Counter(q["presentation_mode"] for q in all_questions),
    Counter({"text_only": 60, "stem_figure": 72, "option_figures": 24, "figure_sequence": 24}),
)
self.assertEqual(
    Counter(q["question_type"] for q in all_questions),
    Counter({"single_choice": 108, "multiple_choice": 48, "multi_blank": 24}),
)
```

场景题组中的 108 道题全部使用 `question_style=scenario`。72 道独立题由 24 道 `calculation` 和 48 道 `concise` 组成；24 道计算题全部使用 `multi_blank`，避免把数值答案伪装成选择题。

风格还要按阶段锁定，防止只满足总量而破坏重点分布：

```python
EXPECTED_STYLE_BY_STAGE = {
    "C1": {"scenario": 14, "calculation": 2, "concise": 6},
    "C2": {"scenario": 12, "calculation": 3, "concise": 3},
    "C3": {"scenario": 16, "calculation": 5, "concise": 5},
    "C4": {"scenario": 16, "calculation": 4, "concise": 4},
    "C5": {"scenario": 12, "calculation": 2, "concise": 4},
    "C6": {"scenario": 18, "calculation": 3, "concise": 3},
    "C7": {"scenario": 16, "calculation": 4, "concise": 4},
    "C8": {"scenario": 2, "calculation": 0, "concise": 10},
    "C9": {"scenario": 2, "calculation": 1, "concise": 9},
}
```

呈现方式按阶段精确锁定：

| 阶段 | `text_only` | `stem_figure` | `option_figures` | `figure_sequence` |
| --- | ---: | ---: | ---: | ---: |
| C1 | 8 | 10 | 2 | 2 |
| C2 | 6 | 8 | 3 | 1 |
| C3 | 9 | 10 | 4 | 3 |
| C4 | 6 | 10 | 4 | 4 |
| C5 | 6 | 7 | 2 | 3 |
| C6 | 7 | 9 | 3 | 5 |
| C7 | 6 | 10 | 4 | 4 |
| C8 | 5 | 5 | 1 | 1 |
| C9 | 7 | 3 | 1 | 1 |

每个 C1-C8 二级节点至少有两道配图题；C9 保持少量配图覆盖选修方法。

- [ ] **Step 3: 写图像引用与选项路由测试**

测试读取 manifest 并按呈现方式检查：

```python
if mode == "text_only":
    self.assertNotIn("figure_refs", question)
    self.assertTrue(all("figure_ref" not in option for option in question.get("options", [])))
elif mode == "stem_figure":
    self.assertEqual(len(question["figure_refs"]), 1)
elif mode == "option_figures":
    self.assertNotIn("figure_refs", question)
    self.assertEqual(len(question["options"]), 4)
    self.assertTrue(all(option.get("figure_ref") in diagram_ids for option in question["options"]))
elif mode == "figure_sequence":
    self.assertGreaterEqual(len(question["figure_refs"]), 2)
    self.assertLessEqual(len(question["figure_refs"]), 4)
```

所有配图题要求 `diagram_focus` 非空；同一道 `option_figures` 题的四个 `figure_ref` 不重复；`figure_sequence` 按 JSON 数组顺序解释，不按文件名排序。

- [ ] **Step 4: 写 24 个计算夹具的独立复算测试**

夹具 ID 和数量固定为：

```text
CAL-C1-STATE-01..02
CAL-C2-ELLIPSE-01..03
CAL-C3-WEIGHT-01..03
CAL-C3-CIRCLE-01..02
CAL-C4-LINE-01..02
CAL-C4-INTERSECT-01..02
CAL-C5-WALL-01..02
CAL-C6-CHAIN-01..02
CAL-C6-SAFE-01
CAL-C7-ANGLE-01..02
CAL-C7-COUNT-01..02
CAL-C9-WEDGE-01
```

`EXPECTED_FIXTURE_KINDS` 为：

```python
Counter({
    "state_coordinate": 2,
    "ellipse_axes": 3,
    "weighted_transform": 3,
    "energy_circle": 2,
    "momentum_line": 2,
    "line_circle_intersection": 2,
    "wall_reflection": 2,
    "state_chain": 2,
    "terminal_sector": 1,
    "equal_angle": 2,
    "angle_count": 2,
    "wedge_angle": 1,
})
```

夹具的阶段计数固定为 `C1=2、C2=3、C3=5、C4=4、C5=2、C6=3、C7=4、C8=0、C9=1`，并与每道 `calculation` 题的归属节点一致。

测试分别从质量、速度、动量和能量重算期望结果。圆线交点使用二次方程重算两个解并同时检查能量圆和动量线；状态链逐事件重算物块弹性碰撞与墙反射；角度计数检查 `theta=atan(sqrt(m/M))` 和每步 `2*theta`。

- [ ] **Step 5: 添加文案质量和物理边界守卫**

沿用 A/B 已接受的标题模板、依赖上一题、选项位置和无关干扰项守卫，并新增：

```python
FORBIDDEN_GRAPH_CONFUSION = (
    "状态点就是物块的位置",
    "换刻度改变了物块速度",
    "动量线就是运动轨迹",
    "圆上的颜色决定碰撞次数",
)
ANGLE_AMBIGUITY = re.compile(r"(?<!2)θ推进|间隔θ(?!与)|圆心角就是θ")
```

凡题目出现 `x`、`y` 坐标，题干或关联图的 manifest 必须给出坐标体系。C7 题必须明确所问是弦方向角、圆周角、圆心角、`theta` 或 `2theta`。C9 题全部满足 `curriculum_scope=elective`，C1-C8 全部为 `core`。

每题只设置一个主要判断目标；多选题只能组合紧密相关的两个结论。题干禁止生硬复述节点标题。解析必须直接点名公式、坐标、点或几何关系，不依赖选项位置和颜色。

- [ ] **Step 6: 编写严格 C 题源 Schema**

根对象要求与 A/B 同类字段，并精确锁定 37 个 quota、6 个 source、24 个 fixture、12 个 scenario 和 72 个 standalone。问题公共字段新增：

```json
{
  "curriculum_scope": {"enum": ["core", "elective"]},
  "presentation_mode": {"enum": ["text_only", "stem_figure", "option_figures", "figure_sequence"]},
  "figure_refs": {"type": "array", "minItems": 1, "maxItems": 4, "items": {"type": "string"}},
  "diagram_focus": {"type": "string", "minLength": 1}
}
```

选项对象允许可选 `figure_ref`。使用条件分支锁定四种呈现方式；使用题型分支锁定四选项、答案数量和多空填空；计算题必须引用一个夹具；场景题要求 `ask` 且禁止 `prompt`，独立题要求 `prompt` 且禁止 `ask`。

- [ ] **Step 7: 运行题源测试并确认 RED**

```powershell
python -m unittest tests.test_question_source_c -v
```

Expected: 因 C 题源与 Schema 缺失而失败。

- [ ] **Step 8: 先编写来源目录与 24 个夹具**

`source_catalog` 保存 `video-main`、`openstax-ellipse`、`openstax-angles`、`openstax-unit-circle`、`openstax-momentum`、`openstax-elastic` 及 Task 1 Step 5 的六个精确地址。每个场景保存 `source_refs`；若主视频与外部材料表述边界不同，把差异写入 `author_notes`，不直接覆盖视频叙事。每个夹具保存 `id`、`node_id`、`kind`、显式输入和 `expected`；答案优先使用整数、有限小数或项目已接受的根式文本。每道计算题只引用归属节点相同的夹具。

- [ ] **Step 9: 编写 C1-C3 的 66 道题**

按配额写完 `SC-C1-STATE`、`SC-C2-ELLIPSE`、`SC-C3-SCALE` 及对应 24 道独立题。重点检查：速度坐标与真实位置的区别、椭圆长短轴与质量关系、乘 `sqrt(mass)` 的必要性、缩放前后状态一一对应。

Run:

```powershell
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_c1_c3_checkpoint -v
```

Expected: C1-C3 共 66 题，风格、图像引用、夹具和逐节点配额均通过。

- [ ] **Step 10: 编写 C4-C6 的 66 道题**

按配额写完 `SC-C4-CHORD`、`SC-C5-WALL`、`SC-C6-CHAIN`、`SC-C6-SAFE` 及对应 20 道独立题。动量线使用 `sqrt(M)*x+sqrt(m)*y=P`，斜率使用 `-sqrt(M/m)`；物块碰撞只在能量圆与同一动量线的两个交点间跳转；墙碰撞只改变 `y` 符号；终止区使用当前坐标体系推导的不等式。

Run:

```powershell
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_c4_c6_checkpoint -v
```

Expected: C4-C6 共 66 题，事件链每步能对应真实碰撞或终止事件。

- [ ] **Step 11: 编写 C7-C9 的 48 道题**

按配额写完 `SC-C7-ANGLE`、`SC-C7-COUNT`、`SC-C8-LEGEND`、`SC-C9-WEDGE`、`SC-C9-UNFOLD` 及对应 28 道独立题。C7 区分 `theta` 与 `2theta`；C8 只做图例关系整合；C9 明确使用质量加权位置坐标并标为选修。

Run:

```powershell
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_c7_c9_checkpoint -v
```

Expected: C7-C9 共 48 题，C9 恰有 12 道选修题。

- [ ] **Step 12: 运行完整题源验证**

```powershell
python -m unittest tests.test_question_source_c -v
$json = Get-Content -Raw content/courses/collision-pi/question-source-c.json
if (-not (Test-Json -Json $json -SchemaFile schemas/objective_question_source_c.schema.json)) { throw 'C source schema failed' }
```

Expected: 总计 180 题，逐节点、场景、风格、题型、呈现、课程层级和夹具分布全部精确通过。

- [ ] **Step 13: 提交完整 C 题源**

```powershell
git add content/courses/collision-pi/question-source-c.json schemas/objective_question_source_c.schema.json tests/test_question_source_c.py
git commit -m "feat: author collision pi C question source"
```

---

### Task 4: 扩展共享生成器并生成正式 C bank

**Files:**
- Modify: `scripts/collision_pi_question_bank.py:17-149`
- Create: `scripts/generate_collision_pi_c_questions.py`
- Create: `content/courses/collision-pi/question-bank-c.json`
- Modify: `schemas/objective_question_bank.schema.json:1-170`
- Modify: `tests/test_question_bank.py`
- Modify: `tests/test_question_bank_b.py`
- Create: `tests/test_question_bank_c.py`

**Interfaces:**
- Consumes: C 题源、C diagram manifest、现有 A/B 题源和知识节点。
- Produces: `build_bank_from_paths(..., diagram_manifest_path: Path | None = None) -> dict`；A/B 调用结果保持原字节，C bank 带 `diagram_manifest_fingerprint`。

- [ ] **Step 1: 写 C bank 失败测试和 A/B 快照守卫**

`tests/test_question_bank_c.py` 要求：

```python
self.assertEqual(self.bank["section_id"], "C")
self.assertEqual(len(self.bank["questions"]), 180)
self.assertEqual(len(self.bank["question_count_by_node"]), 37)
self.assertEqual(Counter(q["curriculum_scope"] for q in self.questions), Counter({"core": 168, "elective": 12}))
self.assertEqual(Counter(q["presentation_mode"] for q in self.questions), Counter({
    "text_only": 60, "stem_figure": 72, "option_figures": 24, "figure_sequence": 24,
}))
self.assertEqual(self.bank["diagram_manifest_fingerprint"], self.manifest["manifest_fingerprint"])
self.assertEqual(generate_c.build_bank(), self.bank)
```

在 A/B 测试中记录当前 checked-in bank 的完整字节和 `content_fingerprint`，运行 A/B wrapper 后必须一致。

- [ ] **Step 2: 运行聚焦测试并确认 RED**

```powershell
python -m unittest tests.test_question_bank tests.test_question_bank_b tests.test_question_bank_c -v
```

Expected: C wrapper 与 bank 缺失；A/B 现有测试保持通过。

- [ ] **Step 3: 让选项轮换保留图像引用**

修改 `expand_choice_options`，文字和图片作为同一个对象轮换：

```python
rendered = []
for index, option in enumerate(rotated):
    item = {"id": OPTION_IDS[index], "text": option["text"]}
    if option.get("figure_ref"):
        item["figure_ref"] = option["figure_ref"]
    rendered.append(item)
```

答案仍按轮换后的 `correct` 标记生成。新增测试把带图选项旋转 0、1、2、3 位，逐次核对文字、`figure_ref` 和正确答案绑定。

- [ ] **Step 4: 透传 C 专属题目字段**

在 `expand_questions` 中只在源字段存在时添加：

```python
for field in ("curriculum_scope", "presentation_mode", "figure_refs", "diagram_focus"):
    if field in question:
        item[field] = question[field]
```

使用 `copy.deepcopy` 或新列表复制 `figure_refs`，避免正式 bank 与作者源共享可变对象。A/B 源不含这些字段，因此其生成结果字段顺序和字节不变。

- [ ] **Step 5: 校验图像引用并加入 manifest 指纹**

扩展构建函数：

```python
def build_bank_from_paths(
    source_path: Path,
    puzzle_path: Path,
    *,
    section_id: str,
    title: str,
    diagram_manifest_path: Path | None = None,
) -> dict:
```

当提供 manifest 时，读取其 ID 集合，校验题干、序列和选项的每个引用。未知 ID 抛出 `ValueError("unknown diagram reference: <id>")`。在 `questions` 写入 bank 后增加：

```python
bank["diagram_manifest_fingerprint"] = manifest["manifest_fingerprint"]
bank["content_fingerprint"] = content_fingerprint(bank)
```

因为 `content_fingerprint` 只排除自身，manifest 指纹自然进入 canonical payload。

- [ ] **Step 6: 新增 C 薄入口并生成 bank**

```python
SOURCE = ROOT / "content/courses/collision-pi/question-source-c.json"
PUZZLE = ROOT / "content/courses/collision-pi/knowledge-puzzle.json"
MANIFEST = ROOT / "content/courses/collision-pi/diagram-manifest-c.json"
OUTPUT = ROOT / "content/courses/collision-pi/question-bank-c.json"

def build_bank() -> dict:
    return build_bank_from_paths(
        SOURCE,
        PUZZLE,
        section_id="C",
        title="碰撞与π · C板块图文客观题库",
        diagram_manifest_path=MANIFEST,
    )
```

`main()` 使用现有 `write_bank` 写出并报告 180 题。

- [ ] **Step 7: 扩展正式 bank Schema**

根 `section_id` 改为 `A/B/C`，共享 `node_id` 模式改为 `^[ABC]`。option 允许可选 `figure_ref`。C 条件分支要求：

```json
{
  "questions": {"minItems": 180, "maxItems": 180},
  "question_count_by_node": {"minProperties": 37, "maxProperties": 37},
  "diagram_manifest_fingerprint": {"type": "string", "pattern": "^[0-9a-f]{64}$"}
}
```

C 的每题必须有 `curriculum_scope` 和 `presentation_mode`，并按四种呈现方式路由图像字段。C1-C8 的 `curriculum_scope` 只允许 `core`，C9 只允许 `elective`。A/B 分支不新增必填字段。

- [ ] **Step 8: 生成并验证 A/B 无漂移**

```powershell
$aBefore = Get-FileHash content/courses/collision-pi/question-bank-a.json -Algorithm SHA256
$bBefore = Get-FileHash content/courses/collision-pi/question-bank-b.json -Algorithm SHA256
python scripts/generate_collision_pi_a_questions.py
python scripts/generate_collision_pi_b_questions.py
python scripts/generate_collision_pi_c_questions.py
$aAfter = Get-FileHash content/courses/collision-pi/question-bank-a.json -Algorithm SHA256
$bAfter = Get-FileHash content/courses/collision-pi/question-bank-b.json -Algorithm SHA256
if ($aBefore.Hash -ne $aAfter.Hash -or $bBefore.Hash -ne $bAfter.Hash) { throw 'A/B bank drift detected' }
python -m unittest tests.test_question_bank tests.test_question_bank_b tests.test_question_bank_c -v
```

Expected: A/B 哈希不变，C 为 180 题并通过正式 Schema。

- [ ] **Step 9: 提交 C bank 和共享生成扩展**

```powershell
git add scripts/collision_pi_question_bank.py scripts/generate_collision_pi_c_questions.py content/courses/collision-pi/question-bank-c.json schemas/objective_question_bank.schema.json tests/test_question_bank.py tests/test_question_bank_b.py tests/test_question_bank_c.py
git commit -m "feat: generate collision pi C question bank"
```

---

### Task 5: 把作者筛选器升级为 A/B/C 图文编辑器

**Files:**
- Modify: `scripts/build_collision_pi_question_editor.py:9-38`
- Modify: `scripts/collision_pi_question_editor_state.js:1-84`
- Modify: `authoring/collision-pi-question-editor.template.html:1-406`
- Modify: `authoring/collision-pi-question-editor.html`
- Modify: `scripts/validate_question_editor.js:1-56`
- Modify: `scripts/validate_question_editor_state.js:1-143`
- Modify: `tests/test_project_contract.py:48-108`

**Interfaces:**
- Consumes: A=140、B=168、C=180 三个 bank，以及 36 项 C diagram manifest。
- Produces: 单页作者工具，支持板块、知识点、题型、场景、课程层级、配图方式和关键词组合筛选，并能渲染题干图、图片选项与有序图序列。

- [ ] **Step 1: 先让静态验证要求 A/B/C 和图像 manifest**

修改 `validate_question_editor.js`，按元素 ID 读取两个 JSON script：

```javascript
const assert = require('assert');
const banks = JSON.parse(extractScript('embeddedQuestionBanks'));
const manifest = JSON.parse(extractScript('embeddedDiagramManifest'));
assert.equal(banks.A.questions.length, 140);
assert.equal(banks.B.questions.length, 168);
assert.equal(banks.C.questions.length, 180);
assert.equal(manifest.diagrams.length, 36);
assert.equal(banks.C.diagram_manifest_fingerprint, manifest.manifest_fingerprint);
```

同时要求 `questionScopeFilter`、`questionPresentationFilter`、`renderFigure`、`figure_sequence` 和 `.cqe-figure-error` 存在。

- [ ] **Step 2: 添加 Python 构建失败测试**

修改 `test_project_contract.py`，解析生成 HTML 并断言 bank 键为 `{"A", "B", "C"}`、题量为 140/168/180、manifest 为 36 项，且 checked-in HTML 与 `build()` 完全一致。

Run:

```powershell
node scripts/validate_question_editor.js
python -m unittest tests.test_project_contract -v
```

Expected: 旧编辑器缺少 C bank、manifest 和两种 C 筛选器而失败。

- [ ] **Step 3: 确定性嵌入 C bank 和 manifest**

扩展 builder：

```python
BANKS = {
    "A": ROOT / "content/courses/collision-pi/question-bank-a.json",
    "B": ROOT / "content/courses/collision-pi/question-bank-b.json",
    "C": ROOT / "content/courses/collision-pi/question-bank-c.json",
}
DIAGRAM_MANIFEST = ROOT / "content/courses/collision-pi/diagram-manifest-c.json"
```

模板新增 `__DIAGRAM_MANIFEST_JSON__`。bank 和 manifest 两段 JSON 都执行 `.replace("<", "\\u003c")`，并在缺少任一 placeholder 时抛出明确错误。

- [ ] **Step 4: 添加 C 板块和两个附加筛选器**

板块选择器增加 `<option value="C">C 板块</option>`。新增：

```html
<label id="questionScopeFilterField">课程层级
  <select id="questionScopeFilter">
    <option value="all">全部层级</option>
    <option value="core">核心</option>
    <option value="elective">选修</option>
  </select>
</label>
<label id="questionPresentationFilterField">配图方式
  <select id="questionPresentationFilter">
    <option value="all">全部方式</option>
    <option value="text_only">纯文字</option>
    <option value="stem_figure">题干配图</option>
    <option value="option_figures">图片选项</option>
    <option value="figure_sequence">图像序列</option>
  </select>
</label>
```

只在 C 激活时显示这两个 field；切到 A/B 时把值重置为 `all`，避免隐藏筛选条件造成空结果。

- [ ] **Step 5: 建立 manifest 索引和明确错误渲染**

```javascript
const diagramById = new Map(diagramManifest.diagrams.map(item => [item.diagram_id, item]));

function renderFigure(diagramId) {
  const entry = diagramById.get(diagramId);
  if (!entry) return makeFigureError(`未知图像：${diagramId}`);
  const figure = document.createElement('figure');
  const image = document.createElement('img');
  image.src = `../${entry.path}`;
  image.alt = entry.alt_text;
  image.width = entry.width;
  image.height = entry.height;
  figure.append(image, makeCaption(entry));
  return figure;
}
```

作者图注显示 `diagram_id`、`coordinate_system` 和 `caption`。图片 `error` 事件把 figure 替换为 `.cqe-figure-error`，内容为“图像加载失败：<id>”。未知 ID、指纹不匹配和文件加载失败都不能静默空白。

- [ ] **Step 6: 渲染三种图像题**

- `stem_figure`: 在题干文本字段之前渲染唯一 `figure_ref`。
- `option_figures`: 每个选项行在答案控件与文字输入框之间渲染该选项的 `figure_ref`；编辑文字不改变图片绑定。
- `figure_sequence`: 按 `figure_refs` 数组顺序渲染 2 至 4 张图，并显示“图 1”“图 2”等稳定序号。

CSS 使用 `max-width:100%`、`height:auto`、`overflow-wrap:anywhere`。375 px 下图片选项改为单列，图像不横向溢出。

- [ ] **Step 7: 扩展组合筛选和关键词索引**

在现有 node/type/scenario/search 条件后增加：

```javascript
const matchesScope = scopeFilter.value === 'all' || question.curriculum_scope === scopeFilter.value;
const matchesPresentation = presentationFilter.value === 'all' || question.presentation_mode === presentationFilter.value;
```

关键词文本加入题干、选项、`diagram_focus`、图注和 `alt_text`。A/B 没有 C 字段时仍能正常匹配，不要求伪造 `text_only`。

- [ ] **Step 8: 让 C 草稿绑定图像指纹**

在 `isMatchingBank` 中加入：

```javascript
if (
  original.section_id === 'C' &&
  candidate.diagram_manifest_fingerprint !== original.diagram_manifest_fingerprint
) return false;
```

页面启动时先比较 `banks.C.diagram_manifest_fingerprint` 与嵌入 manifest；不一致时禁用 C 板块并显示状态错误。扩展 state validator，检查 C 当前草稿可恢复、错误图像指纹草稿被丢弃、A/B/C 草稿键互不覆盖。

- [ ] **Step 9: 重建并运行静态验证**

```powershell
python scripts/build_collision_pi_question_editor.py
node scripts/validate_question_editor_state.js
node scripts/validate_question_editor.js
python -m unittest tests.test_project_contract -v
```

Expected: Node 报告 A=140、B=168、C=180、36 diagrams；Python 构建一致性通过。

- [ ] **Step 10: 用应用内浏览器做作者工具验收**

使用 `browser:control-in-app-browser` 打开：

```text
http://127.0.0.1:8765/authoring/collision-pi-question-editor.html?section=C&bank=4
```

逐项验证：

- A 显示 20 个承载节点和 140 题，B 显示 22 个承载节点和 168 题，C 显示 37 个承载节点和 180 题。
- C 核心筛选返回 168 题，选修筛选返回 12 题。
- 四种呈现方式分别返回 60、72、24、24 题。
- `SC-C3-SCALE` 返回 16 题，`SC-C6-CHAIN` 返回 10 题，`SC-C7-COUNT` 返回 8 题。
- 题干图、四个图片选项和有序图像序列均可见；作者能编辑文字和答案控件。
- 临时构造不存在的 diagram ID 时出现明确错误卡，恢复正式数据后错误消失。
- C 到 A 到 B 到 C 切换不串节点、场景、隐藏筛选条件或本地草稿。
- 1280 px 与 375 px 均无水平溢出；控制台错误数为 0；图片具有可读的无障碍名称。

- [ ] **Step 11: 提交 A/B/C 图文作者工具**

```powershell
git add scripts/build_collision_pi_question_editor.py scripts/collision_pi_question_editor_state.js authoring/collision-pi-question-editor.template.html authoring/collision-pi-question-editor.html scripts/validate_question_editor.js scripts/validate_question_editor_state.js tests/test_project_contract.py
git commit -m "feat: edit collision pi C visual questions"
```

---

### Task 6: 更新项目事实并完成全量图文验收

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/roadmap.md`
- Modify: `docs/decisions/conversation-decisions.md`
- Modify: `tests/test_project_contract.py`
- Modify: `tests/test_independence.py` only if new runtime/config paths require independence coverage

**Interfaces:**
- Consumes: 最终图像源、36 个 SVG、C 题源、C bank 和 A/B/C 作者工具。
- Produces: 当前项目事实、两轮确定性证据、完整自动化证据、180 题逐读记录和 36 图逐图浏览器验收。

- [ ] **Step 1: 先让当前事实测试要求 C 合同**

在四个当前事实文档中要求以下语句原样出现：

```text
《碰撞与π》知识拼图共 136 个节点：A=27、B=27、C=46、D=36。
A 板块有 20 个承载题目的二级节点，共 140 道客观题。
B 板块有 22 个承载题目的二级节点，共 168 道客观题。
C 板块有 37 个承载题目的二级节点，共 180 道客观题。
C 题库包含 12 个场景题组、24 道计算题和 120 道配图题。
C 图像资产由 10 类模板生成 36 个 SVG 实例。
```

保留对 `144 个节点`、`139 个节点`、`A=32`、`B=30`、`192 道` 和 `每节点 6 道` 的当前事实否定守卫。

- [ ] **Step 2: 运行文档合同并确认 RED**

```powershell
python -m unittest tests.test_project_contract -v
```

Expected: 四个文档因缺少 C 题库与图像资产事实而失败。

- [ ] **Step 3: 更新四个当前文档**

记录 C 图文题库已完成，作者工具支持 A/B/C。路线图把“后续生成 C/D 题库”改为只保留 D；不改变学生运行时、账号、支付、云部署、状态观察题和错题追问 Agent 的既定边界。

- [ ] **Step 4: 连续执行两轮完整构建**

每一轮按同一顺序运行：

```powershell
python scripts/build_collision_pi_knowledge_puzzle.py
python scripts/generate_collision_pi_a_questions.py
python scripts/generate_collision_pi_b_questions.py
python scripts/generate_collision_pi_c_diagrams.py
python scripts/generate_collision_pi_c_questions.py
python scripts/build_collision_pi_question_editor.py
```

两轮分别记录这些文件的 SHA-256：

```text
content/courses/collision-pi/knowledge-puzzle.md
content/courses/collision-pi/question-bank-a.json
content/courses/collision-pi/question-bank-b.json
content/courses/collision-pi/diagram-manifest-c.json
content/courses/collision-pi/question-bank-c.json
authoring/collision-pi-question-editor.html
```

两轮哈希必须逐项一致；A/B bank 哈希还必须与 Task 4 前保存值一致。

- [ ] **Step 5: 运行全量测试、Schema 和静态验证**

```powershell
python -m unittest discover -s tests -v
node scripts/validate_question_editor_state.js
node scripts/validate_question_editor.js
```

使用 `Test-Json` 验证：

```text
knowledge-puzzle.json -> knowledge_puzzle.schema.json
diagram-source-c.json -> collision_pi_diagram_source_c.schema.json
question-source-a.json -> objective_question_source.schema.json
question-source-b.json -> objective_question_source_b.schema.json
question-source-c.json -> objective_question_source_c.schema.json
question-bank-a.json、question-bank-b.json、question-bank-c.json -> objective_question_bank.schema.json
```

Expected: 全部命令退出码为 0，无 Schema 失败，无生成漂移。

- [ ] **Step 6: 逐读 180 道最终题目**

按 C1-C9 顺序阅读正式 bank 中每个完整题干、选项、正确答案、填空接受值和解析。重点审查：

- 每题自包含，不依赖题组上一题答案。
- 状态点不被写成真实位置，缩放不被写成物理状态改变。
- 动量线斜率、能量曲线、交点和墙反射符合声明坐标体系。
- C6 每次跳点对应真实事件，计数口径一致，安全区不等式方向正确。
- C7 区分 `theta`、`2theta`、圆周角和圆心角。
- C9 始终是选修并使用位置坐标，不与速度相空间混图。
- 多选题恰有两个正确选项；选项轮换后图片和答案仍绑定。
- 解析不依赖“A 项”“前两项”等位置措辞，不泄露给学生端。

- [ ] **Step 7: 逐图验收 36 个 SVG 实例**

在应用内浏览器中依次打开 manifest 的 36 个路径，核对物理点位、坐标标签、斜率、箭头、角标、图注和无障碍文字。每类模板至少在 1280 px 和 375 px 各检查一个实例；`scale_pair` 必须清楚区分左右坐标体系；灰度下点形和线型仍可区分。

- [ ] **Step 8: 在最终构建上重复作者工具浏览器验收**

重复 Task 5 Step 10 的全部计数、筛选、渲染、草稿、控制台和视口检查。最终截图至少覆盖：题干配图、图片选项、图像序列、C9 选修筛选和 375 px 窄屏。

- [ ] **Step 9: 检查仓库完整性并提交文档守卫**

```powershell
git diff --check
git status --short
git add AGENTS.md README.md docs/roadmap.md docs/decisions/conversation-decisions.md tests/test_project_contract.py
git commit -m "docs: record collision pi C visual question contract"
```

若 `tests/test_independence.py` 没有有意修改，不加入提交。提交后重新运行全量 Python 测试、两个 Node 验证器和 `git status --short --branch`。

---

## Final Verification Checklist

- [ ] C 节点仍为 46，总知识拼图仍为 136 个节点。
- [ ] diagram source 恰有 36 项、10 类模板和 3 个坐标体系。
- [ ] 36 个 SVG 可解析、无脚本、哈希稳定且与 manifest 一致。
- [ ] C 题源与正式 bank 均为 180 题、37 个配额键、12 个场景和 24 个计算夹具。
- [ ] 核心 168、选修 12；风格 108/24/48；呈现 60/72/24/24。
- [ ] 120 道配图题全部引用存在的图像，图片选项轮换后答案不漂移。
- [ ] C bank 的 manifest 指纹进入 `content_fingerprint`，旧图像草稿被拒绝。
- [ ] A bank 仍为 140 题且字节不变，B bank 仍为 168 题且字节不变。
- [ ] 作者工具显示 A/B/C，全部组合筛选和三种图像渲染正常。
- [ ] 180 道题逐读完成，36 张图逐图验收完成。
- [ ] 两轮完整构建哈希一致，全量 Python、Schema、Node 和浏览器验收通过。
- [ ] 工作树无意外修改，最终分支状态可供代码审查。
