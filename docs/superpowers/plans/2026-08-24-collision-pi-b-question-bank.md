# Collision & Pi B Question Bank Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorder section B into 27 nodes, author and generate a 168-question B objective bank, and extend the author editor to filter both A and B without regressing the accepted A bank.

**Architecture:** Keep `knowledge-puzzle.json` as the node source of truth and add `question-source-b.json` as the reviewed B author source. Extract the section-neutral expansion logic from the A generator, keep thin A/B entry points, generate separate formal banks, and embed both banks in one author editor with section-scoped filters and drafts.

**Tech Stack:** Python 3.13 standard library, JSON Schema Draft 2020-12, HTML/CSS/vanilla JavaScript, Node.js static validation, Python `unittest`, local UTF-8 HTTP server.

**Spec:** `docs/superpowers/specs/2026-08-24-collision-pi-b-question-bank-design.md`

## Global Constraints

- Preserve the accepted A contract exactly: 27 A nodes, 20 assessed A nodes, 140 A questions, 13 A scenario families, 8 A calculations, and 44 A concise questions.
- Replace B with exactly 5 stage nodes and 22 assessed nodes, 27 B nodes total; course totals become A=27, B=27, C=46, D=36, total 136.
- Generate exactly 168 B objective questions with `scenario=104`, `calculation=32`, and `concise=32`.
- Use the exact B node titles, roles, summaries, quotas, migration mapping, 15 scenario IDs, and scenario allocations from the spec.
- Every question and learning record reference remains `node_id`-based; stage nodes do not carry questions.
- Status-observation questions remain disabled and separate from objective questions.
- Author-side and judging-side artifacts may contain answers; the student delivery policy must keep `reveal_answer_after_wrong=false`.
- Every scenario item is self-contained after `context + ask` composition and never depends on another answer.
- State the positive direction, system, and time interval whenever they affect the answer.
- Explanations name quantities, values, or relations rather than source-option positions.
- Use only the standard library and existing project dependencies; do not add a package manager or runtime dependency.

## File Structure

### Node model

- Modify `content/courses/collision-pi/knowledge-puzzle.json`: replace only the B segment with the approved 27-node order and bump the puzzle version.
- Regenerate `content/courses/collision-pi/knowledge-puzzle.md` with the existing builder.
- Modify `tests/test_knowledge_puzzle.py`: lock B order, records, counts, and Markdown parity.
- Modify `tests/test_project_contract.py`: lock the new course totals and current documentation facts.

### Authored B source

- Create `content/courses/collision-pi/question-source-b.json`: B quotas, source catalog, 32 fixtures, 15 scenarios, and 32 concise questions.
- Create `schemas/objective_question_source_b.schema.json`: strict B-specific Draft 2020-12 contract.
- Create `tests/test_question_source_b.py`: exact source allocation, physics, wording, payload, and schema tests.

### Shared generation and formal bank

- Create `scripts/collision_pi_question_bank.py`: section-neutral option rotation, source expansion, quota checks, and bank assembly.
- Modify `scripts/generate_collision_pi_a_questions.py`: thin compatible A wrapper over the shared module.
- Create `scripts/generate_collision_pi_b_questions.py`: thin B wrapper.
- Create `content/courses/collision-pi/question-bank-b.json`: generated B bank.
- Modify `schemas/objective_question_bank.schema.json`: exact conditional contracts for A=140 and B=168.
- Modify `tests/test_question_bank.py`: keep A coverage and common-builder parity.
- Create `tests/test_question_bank_b.py`: B generation, schema, IDs, quotas, and checked-in parity.

### Dual-section author editor

- Modify `authoring/collision-pi-question-editor.template.html`: section selector, section-aware filters, metadata, summaries, and draft storage.
- Modify `scripts/build_collision_pi_question_editor.py`: embed an `{A, B}` bank map.
- Regenerate `authoring/collision-pi-question-editor.html`.
- Modify `scripts/validate_question_editor.js`: parse two embedded banks and validate A=140/B=168 plus the section UI.
- Modify `tests/test_project_contract.py`: assert the checked-in editor equals `build()`.

### Documentation

- Modify `AGENTS.md`, `README.md`, `docs/roadmap.md`, and `docs/decisions/conversation-decisions.md`: state 136 nodes and the exact A/B objective-bank contracts while preserving product boundaries.

---

### Task 1: Replace the B Node Contract and Preserve A/C/D

**Files:**
- Modify: `content/courses/collision-pi/knowledge-puzzle.json`
- Modify: `content/courses/collision-pi/knowledge-puzzle.md`
- Modify: `tests/test_knowledge_puzzle.py`
- Modify: `tests/test_project_contract.py`

**Interfaces:**
- Consumes: `render_markdown(puzzle: dict) -> str` from `scripts/build_collision_pi_knowledge_puzzle.py`.
- Produces: the ordered set of 22 assessed B IDs and titles consumed by the source, generator, bank schema, and editor.

- [ ] **Step 1: Add the exact B contract constants and failing tests**

Add these constants to `tests/test_knowledge_puzzle.py`:

```python
EXPECTED_B_IDS = (
    "B1", "B1.1", "B1.2", "B1.3", "B1.4",
    "B2", "B2.1", "B2.2", "B2.3", "B2.4",
    "B3", "B3.1", "B3.2", "B3.3", "B3.4", "B3.5",
    "B4", "B4.1", "B4.2", "B4.3", "B4.4", "B4.5",
    "B5", "B5.1", "B5.2", "B5.3", "B5.4",
)

EXPECTED_B_QUOTAS = {
    "B1.1": 6, "B1.2": 6, "B1.3": 6, "B1.4": 6,
    "B2.1": 8, "B2.2": 10, "B2.3": 8, "B2.4": 6,
    "B3.1": 6, "B3.2": 8, "B3.3": 8, "B3.4": 10, "B3.5": 6,
    "B4.1": 10, "B4.2": 12, "B4.3": 10, "B4.4": 8, "B4.5": 6,
    "B5.1": 8, "B5.2": 8, "B5.3": 8, "B5.4": 4,
}
```

Add tests that select B records in source order and assert:

```python
def test_b_has_five_stages_and_twenty_two_assessed_nodes(self):
    b_nodes = [node for node in self.nodes if node["board"] == "B"]
    self.assertEqual(tuple(node["id"] for node in b_nodes), EXPECTED_B_IDS)
    self.assertEqual(sum(node["depth"] == 1 for node in b_nodes), 5)
    self.assertEqual(sum(node["depth"] == 2 for node in b_nodes), 22)

def test_exact_node_and_board_counts(self):
    self.assertEqual(
        Counter(node["board"] for node in self.nodes),
        Counter({"A": 27, "B": 27, "C": 46, "D": 36}),
    )
    self.assertEqual(len(self.nodes), 136)
```

Create an `EXPECTED_B_RECORDS` tuple containing every exact ID, parent, depth, title, role, and summary from spec section 3.2, then compare the projected JSON records to it. Preserve the existing exact A record assertion.

- [ ] **Step 2: Run the focused tests and confirm RED**

Run:

```powershell
python -m unittest tests.test_knowledge_puzzle tests.test_project_contract -v
```

Expected: failures report the old 30-node B structure and old total 139; existing A assertions continue to pass.

- [ ] **Step 3: Replace only the B JSON segment**

Copy all 27 exact B records from spec section 3.2 into `knowledge-puzzle.json` in the documented order. Preserve every A/C/D record value and relative order. Set the puzzle version to `3.0.0` because B node IDs and total counts change.

Each stage record uses `depth: 1`; each assessed record uses `depth: 2` and its stage ID as the existing hierarchy field used by the file. Do not introduce a second parent-field spelling.

- [ ] **Step 4: Regenerate Markdown and verify GREEN**

Run:

```powershell
python scripts/build_collision_pi_knowledge_puzzle.py
python -m unittest tests.test_knowledge_puzzle tests.test_project_contract -v
```

Expected: the builder reports 136 nodes; all focused tests pass. If the project-contract documentation assertions remain red because they still require 139, update only the data-contract assertion in this task; current-doc copy is updated in Task 5.

- [ ] **Step 5: Verify no runtime B reference is dangling**

Add a repository scan test that loads every current `question-bank-*.json` and `question-source-*.json` file and asserts that any `node_id` beginning with `B` is in `EXPECTED_B_QUOTAS`. At this point no B question asset exists, so the test proves the migration has no hidden consumer.

- [ ] **Step 6: Commit the node contract**

```powershell
git add content/courses/collision-pi/knowledge-puzzle.json content/courses/collision-pi/knowledge-puzzle.md tests/test_knowledge_puzzle.py tests/test_project_contract.py
git commit -m "feat: reorder collision pi B nodes"
```

---

### Task 2: Author the Strict 168-Question B Source

**Files:**
- Create: `content/courses/collision-pi/question-source-b.json`
- Create: `schemas/objective_question_source_b.schema.json`
- Create: `tests/test_question_source_b.py`

**Interfaces:**
- Consumes: the exact 22 assessed B node IDs/titles from Task 1 and the source-question field conventions already used by A.
- Produces: `question-source-b.json` with exact quotas, 5 source references, 32 executable fixtures, 15 ordered scenarios, 136 grouped questions, and 32 standalone questions.

- [ ] **Step 1: Write the failing source-contract tests**

Create `tests/test_question_source_b.py` with these exact constants:

```python
EXPECTED_QUOTAS = {
    "B1.1": 6, "B1.2": 6, "B1.3": 6, "B1.4": 6,
    "B2.1": 8, "B2.2": 10, "B2.3": 8, "B2.4": 6,
    "B3.1": 6, "B3.2": 8, "B3.3": 8, "B3.4": 10, "B3.5": 6,
    "B4.1": 10, "B4.2": 12, "B4.3": 10, "B4.4": 8, "B4.5": 6,
    "B5.1": 8, "B5.2": 8, "B5.3": 8, "B5.4": 4,
}

EXPECTED_SCENARIO_NODE_COUNTS = {
    "SC-B1-RECORD": {"B1.1": 4, "B1.4": 4},
    "SC-B1-IMPULSE": {"B1.2": 4},
    "SC-B1-ENERGY": {"B1.3": 4},
    "SC-B2-BOUNDARY": {"B2.1": 6, "B2.4": 4},
    "SC-B2-CONSERVE": {"B2.2": 8},
    "SC-B2-ELASTICITY": {"B2.3": 6},
    "SC-B3-EQUATIONS": {"B3.1": 4, "B3.2": 6, "B3.3": 6},
    "SC-B3-RELATIVE": {"B3.4": 8},
    "SC-B3-RESTITUTION": {"B3.5": 4},
    "SC-B4-SOLVE": {"B4.1": 9, "B4.2": 11},
    "SC-B4-RATIO": {"B4.3": 9},
    "SC-B4-CHECK": {"B4.4": 7, "B4.5": 5},
    "SC-B5-CHAIN": {"B5.1": 8, "B5.2": 8},
    "SC-B5-TERMINAL": {"B5.3": 8},
    "SC-B5-GEOMETRY": {"B5.4": 3},
}
```

Tests must assert all of the following directly:

```python
self.assertEqual(source["section_id"], "B")
self.assertEqual(source["node_quotas"], EXPECTED_QUOTAS)
self.assertEqual(sum(EXPECTED_QUOTAS.values()), 168)
self.assertEqual(len(source["scenarios"]), 15)
self.assertEqual(len(scenario_questions), 136)
self.assertEqual(len(source["standalone_questions"]), 32)
self.assertEqual(
    Counter(q["question_style"] for q in all_questions),
    Counter({"scenario": 104, "calculation": 32, "concise": 32}),
)
```

Also assert scenario order equals the dictionary insertion order, every scenario's node counter equals its expected allocation, every `(node_id, key)` is unique, every question has difficulty 1—3, and each question type routes to exactly one answer payload.

- [ ] **Step 2: Add executable wording and quality guards**

Reuse the accepted A behavior as explicit B tests rather than importing A test constants. Add patterns that reject:

```python
TITLE_TEMPLATES = ("关于“", "判断“", "下列哪项最符合“")
DEPENDENT_REFERENCE = re.compile(
    r"(?:(?:上|前)(?:一)?(?:问|题)|(?:前面|刚才)(?:的)?(?:问|题)|"
    r"(?:继续|沿用|承接)(?:上|前)(?:一)?(?:问|题))"
)
OPTION_POSITION = re.compile(
    r"(?:第[一二三四](?:[、，和及与][一二三四])?项|"
    r"[前后][一二两三四](?:项|组|种状态)|第[一二三四]个选项|第[一二三四]种会)"
)
IRRELEVANT_DISTRACTORS = ("颜色", "编号", "字体", "质量都变为零", "时间停止")
```

Assert `DEPENDENT_REFERENCE` does not match valid event phrases such as `第一次碰撞后、第二次碰撞前`. Add targeted checks that prompts requiring direction contain a positive-direction sentence, and prompts applying conservation state both the selected system and research interval in either the shared context or the ask.

- [ ] **Step 3: Define the 32 fixture contracts and physics recomputation tests**

Use exactly these fixture-kind counts:

```python
EXPECTED_FIXTURE_KINDS = Counter({
    "momentum_impulse": 4,
    "energy_audit": 4,
    "elastic_1d": 16,
    "restitution_1d": 4,
    "collision_chain": 4,
})
```

Implement independent recomputation in the test:

```python
if kind == "momentum_impulse":
    p0 = fixture["mass"] * fixture["u"]
    p1 = fixture["mass"] * fixture["v"]
    self.assertAlmostEqual(fixture["expected"]["p_before"], p0)
    self.assertAlmostEqual(fixture["expected"]["p_after"], p1)
    self.assertAlmostEqual(fixture["expected"]["delta_p"], p1 - p0)
    self.assertAlmostEqual(fixture["expected"]["impulse"], p1 - p0)
elif kind == "energy_audit":
    before = sum(0.5 * m * u ** 2 for m, u in zip(fixture["masses"], fixture["before"]))
    after = sum(0.5 * m * v ** 2 for m, v in zip(fixture["masses"], fixture["after"]))
    self.assertAlmostEqual(fixture["expected"]["k_before"], before)
    self.assertAlmostEqual(fixture["expected"]["k_after"], after)
    self.assertAlmostEqual(fixture["expected"]["delta_k"], after - before)
elif kind in {"elastic_1d", "restitution_1d"}:
    m1, m2 = fixture["m1"], fixture["m2"]
    u1, u2 = fixture["u1"], fixture["u2"]
    e = 1 if kind == "elastic_1d" else fixture["e"]
    v1 = (m1 * u1 + m2 * u2 - m2 * e * (u1 - u2)) / (m1 + m2)
    v2 = (m1 * u1 + m2 * u2 + m1 * e * (u1 - u2)) / (m1 + m2)
    self.assertAlmostEqual(fixture["expected"]["v1"], v1)
    self.assertAlmostEqual(fixture["expected"]["v2"], v2)
    self.assertAlmostEqual(m1 * u1 + m2 * u2, m1 * v1 + m2 * v2)
    self.assertAlmostEqual(v2 - v1, e * (u1 - u2))
elif kind == "collision_chain":
    self.assert_chain_states_match_event_updates(fixture)
```

`assert_chain_states_match_event_updates` must recompute every object-object collision with the elastic formula, every fixed-wall event by negating the striking object's velocity, and the terminal result from the stated relative-position/velocity condition.

- [ ] **Step 4: Write the strict B source Schema**

Create a Draft 2020-12 schema with this top-level contract:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "course_id", "section_id", "version", "node_quotas", "source_catalog",
    "calculation_fixtures", "scenarios", "standalone_questions"
  ],
  "properties": {
    "course_id": {"const": "collision-pi"},
    "section_id": {"const": "B"},
    "version": {"const": "1.0.0"}
  }
}
```

Lock all 22 quota property names and values, all 15 scenario IDs in order, exactly 32 fixtures, exactly 32 standalone questions, and the five source IDs `video-main`, `openstax-momentum`, `openstax-impulse`, `openstax-conservation`, and `openstax-elastic`.

Define closed fixture branches for `momentum_impulse`, `energy_audit`, `elastic_1d`, `restitution_1d`, and `collision_chain`. Preserve the accepted A payload routing: scenario questions require `ask` and forbid `prompt`; standalone questions require `prompt` and forbid `ask`; choice questions require four options and forbid blanks; multi-blank requires blanks and forbids options; calculations require `calculation_fixture_id`.

Extend B's `variant_axis` enum with the existing A values plus `impulse`, `energy`, `conservation`, `equation_setup`, `solution_method`, `restitution`, `limit`, and `state_geometry`.

- [ ] **Step 5: Run the source tests and confirm RED**

Run:

```powershell
python -m unittest tests.test_question_source_b -v
```

Expected: import/setup failure reports missing `question-source-b.json` before authored content exists.

- [ ] **Step 6: Author the source catalog and all 32 fixtures first**

Use `sources/theory/弹性碰撞与π.txt` as `video-main` and these existing textbook routes for cross-checking:

```text
https://openstax.org/books/college-physics/pages/8-1-linear-momentum-and-force
https://openstax.org/books/college-physics/pages/8-2-impulse
https://openstax.org/books/college-physics/pages/8-3-conservation-of-momentum
https://openstax.org/books/college-physics/pages/8-4-elastic-collisions-in-one-dimension
```

Give every fixture a stable ID following `CAL-B1-MI-01`, `CAL-B1-EA-01`, `CAL-B4-EL-01`, `CAL-B3-RE-01`, or `CAL-B5-CH-01`, one owning `node_id`, one fixture kind, explicit inputs, and independently checked expected values. Choose integer or simple-fraction results where possible.

- [ ] **Step 7: Author B1/B2 scenarios as the first saved checkpoint**

Write `SC-B1-RECORD`, `SC-B1-IMPULSE`, `SC-B1-ENERGY`, `SC-B2-BOUNDARY`, `SC-B2-CONSERVE`, and `SC-B2-ELASTICITY` with their exact allocations. They total 40 grouped questions and contain exactly 8 calculation questions.

Use experiment tables and concrete collision intervals. Questions must distinguish signed momentum from scalar kinetic energy, paired internal impulses from system momentum, and wall/ground external impulse from object-object internal impulse.

Run a focused test that selects only B1/B2 scenario IDs and checks counts, payloads, fixture references, wording, and physics. Save this checkpoint before authoring B3/B4.

- [ ] **Step 8: Author B3 scenarios as the second saved checkpoint**

Write `SC-B3-EQUATIONS`, `SC-B3-RELATIVE`, and `SC-B3-RESTITUTION`: 28 grouped questions with exactly 8 calculations.

At least one equation-setup question must present each of these velocity patterns: moving into a stationary target, head-on approach, same-direction chase, and a stated non-collision case. Relative-speed questions must keep the sign convention explicit. Restitution questions must distinguish `e=1`, `0<e<1`, and `e=0` without implying that momentum conservation alone fixes `e`.

- [ ] **Step 9: Author B4 scenarios as the third saved checkpoint**

Write `SC-B4-SOLVE`, `SC-B4-RATIO`, and `SC-B4-CHECK`: 41 grouped questions with exactly 12 calculations.

The 20-question solve family must cover both elimination and difference-of-squares reasoning, the general formula, and numeric substitution. The ratio family must cover equal masses, 1:3, 3:1, and a large-mass limit. The check family must diagnose sign errors, use approach/separation conditions to reject a wrong root, and verify momentum, kinetic energy, relative speed, and dimensions.

- [ ] **Step 10: Author B5 scenarios and all concise questions**

Write `SC-B5-CHAIN`, `SC-B5-TERMINAL`, and `SC-B5-GEOMETRY`: 27 grouped questions with exactly 4 calculations. Reuse one initial state to ask first collision, wall reflection, second collision, next-event condition, terminal condition, collision count, and a large-block-stops special case; each rendered prompt remains self-contained.

Add the exact 32 standalone distribution from spec section 4.2. Concise questions cover definitions and boundary distinctions that do not need a long shared context; do not duplicate a grouped numeric calculation as a short question.

- [ ] **Step 11: Run complete B source verification**

Run:

```powershell
python -m unittest tests.test_question_source_b -v
$json = Get-Content -Raw content/courses/collision-pi/question-source-b.json
if (-not (Test-Json -Json $json -SchemaFile schemas/objective_question_source_b.schema.json)) { throw 'B source schema failed' }
```

Expected: every B source test and the formal Schema pass; exact totals are 168, 136 grouped, 32 concise, 32 calculation, and 15 scenarios.

- [ ] **Step 12: Commit the complete authored source**

Commit checkpoint changes during Steps 7—10 with scoped messages, then finish the source task with:

```powershell
git add content/courses/collision-pi/question-source-b.json schemas/objective_question_source_b.schema.json tests/test_question_source_b.py
git commit -m "feat: author collision pi B question source"
```

The task review range starts at Task 1's final commit and includes every B-source checkpoint commit.

---

### Task 3: Extract Shared Generation and Produce the B Bank

**Files:**
- Create: `scripts/collision_pi_question_bank.py`
- Modify: `scripts/generate_collision_pi_a_questions.py`
- Create: `scripts/generate_collision_pi_b_questions.py`
- Create: `content/courses/collision-pi/question-bank-b.json`
- Modify: `schemas/objective_question_bank.schema.json`
- Modify: `tests/test_question_bank.py`
- Create: `tests/test_question_bank_b.py`

**Interfaces:**
- Consumes: both authored source files and the assessed-node catalog from `knowledge-puzzle.json`.
- Produces: `build_bank_from_paths(source_path: Path, puzzle_path: Path, *, section_id: str, title: str) -> dict`, plus compatible zero-argument `build_bank()` functions in both entry-point modules.

- [ ] **Step 1: Add failing shared-builder and B-bank tests**

In `tests/test_question_bank.py`, keep the accepted A assertions and add a behavior-parity test that compares the current A wrapper output to the checked-in A bank.

In `tests/test_question_bank_b.py`, define:

```python
ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "content/courses/collision-pi/question-bank-b.json"
EXPECTED_QUOTAS = {
    "B1.1": 6, "B1.2": 6, "B1.3": 6, "B1.4": 6,
    "B2.1": 8, "B2.2": 10, "B2.3": 8, "B2.4": 6,
    "B3.1": 6, "B3.2": 8, "B3.3": 8, "B3.4": 10, "B3.5": 6,
    "B4.1": 10, "B4.2": 12, "B4.3": 10, "B4.4": 8, "B4.5": 6,
    "B5.1": 8, "B5.2": 8, "B5.3": 8, "B5.4": 4,
}

def test_b_bank_contract(self):
    self.assertEqual(self.bank["section_id"], "B")
    self.assertEqual(self.bank["question_count_by_node"], EXPECTED_QUOTAS)
    self.assertEqual(len(self.bank["questions"]), 168)
    self.assertEqual(
        Counter(q["question_style"] for q in self.bank["questions"]),
        Counter({"scenario": 104, "calculation": 32, "concise": 32}),
    )

def test_checked_in_b_bank_matches_generator(self):
    self.assertEqual(generate_b.build_bank(), self.bank)
```

Also test exact node-title parity with the puzzle, unique IDs/prompts, delivery policy, answer cardinality, scenario metadata, fixture propagation, option rotation, and rejection of a B question pointing at a stage node or A node.

- [ ] **Step 2: Run focused tests and confirm RED**

```powershell
python -m unittest tests.test_question_bank tests.test_question_bank_b -v
```

Expected: B imports/files are missing and the shared-builder interface does not exist; existing A tests remain green.

- [ ] **Step 3: Extract the section-neutral builder**

Create `scripts/collision_pi_question_bank.py` with these public functions:

```python
OPTION_IDS = ["A", "B", "C", "D"]

def rotate(values: list[T], offset: int) -> list[T]:
    offset %= len(values)
    return values[offset:] + values[:offset]

def expand_choice_options(
    options: list[dict], offset: int
) -> tuple[list[dict], list[str]]:
    rotated = rotate(options, offset)
    rendered = [
        {"id": OPTION_IDS[index], "text": option["text"]}
        for index, option in enumerate(rotated)
    ]
    answers = [
        OPTION_IDS[index]
        for index, option in enumerate(rotated)
        if option["correct"]
    ]
    return rendered, answers

def expand_questions(source: dict, puzzle: dict, section_id: str) -> list[dict]:
    titles = {
        node["id"]: node["title"]
        for node in puzzle["nodes"]
        if node["board"] == section_id and node["depth"] == 2
    }
    source_items = [
        (scenario, question)
        for scenario in source["scenarios"]
        for question in scenario["questions"]
    ] + [(None, question) for question in source["standalone_questions"]]
    expanded = []
    for index, (scenario, question) in enumerate(source_items):
        node_id = question["node_id"]
        if node_id not in titles:
            raise ValueError(f"question references non-assessed node: {node_id}")
        prompt = question["prompt"] if scenario is None else (
            f"{scenario['context']}\n\n{question['ask']}"
        )
        item = {
            "id": f"cp-{node_id.lower().replace('.', '-')}-{question['key']}",
            "node_id": node_id,
            "node_title": titles[node_id],
            "question_type": question["question_type"],
            "question_style": question["question_style"],
            "assessment_kind": "objective",
            "difficulty": question["difficulty"],
            "prompt": prompt,
            "event_stage": question["event_stage"],
            "variant_axis": question["variant_axis"],
            "explanation": question["explanation"],
            "enabled": True,
            "revision": 0,
            "author_notes": question.get("author_notes", ""),
        }
        if scenario is not None:
            item["scenario_id"] = scenario["id"]
            item["source_refs"] = scenario["source_refs"]
        if question.get("calculation_fixture_id"):
            item["calculation_fixture_id"] = question["calculation_fixture_id"]
        if "options" in question:
            item["options"], item["correct_answers"] = expand_choice_options(
                question["options"], index
            )
        else:
            item["blanks"] = question["blanks"]
        expanded.append(item)
    return expanded

def build_bank_from_paths(
    source_path: Path,
    puzzle_path: Path,
    *,
    section_id: str,
    title: str,
) -> dict:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    puzzle = json.loads(puzzle_path.read_text(encoding="utf-8"))
    if source["section_id"] != section_id:
        raise ValueError(
            f"source section {source['section_id']} does not match {section_id}"
        )
    questions = expand_questions(source, puzzle, section_id)
    actual = Counter(question["node_id"] for question in questions)
    expected = Counter(source["node_quotas"])
    if actual != expected:
        raise ValueError(
            f"question quota mismatch: actual={dict(actual)}, expected={dict(expected)}"
        )
    return {
        "$schema": "../../../schemas/objective_question_bank.schema.json",
        "course_id": "collision-pi",
        "section_id": section_id,
        "title": title,
        "version": source["version"],
        "question_count_by_node": source["node_quotas"],
        "delivery_policy": {
            "reveal_answer_after_wrong": False,
            "wrong_answer_action": "error_followup_agent",
            "correct_answer_actions": ["next_question", "error_followup_agent"],
        },
        "status_assessment": {
            "enabled": False,
            "note": "按当前产品决定暂缓设计和生成。",
        },
        "questions": questions,
    }

def write_bank(bank: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(bank, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
```

Move the accepted A expansion behavior without changing field order, ID generation, option rotation, answer mapping, or delivery policy. Select assessed titles with `node["board"] == section_id and node["depth"] == 2`. Reject a source whose `section_id` disagrees with the wrapper, and reject actual quota counters that differ from `node_quotas`.

- [ ] **Step 4: Convert A to a thin compatible wrapper**

Keep `SOURCE`, `PUZZLE`, `OUTPUT`, `build_bank()`, and `main()` so existing imports and commands remain valid:

```python
def build_bank() -> dict:
    return build_bank_from_paths(
        SOURCE,
        PUZZLE,
        section_id="A",
        title="碰撞与π · A板块客观题库",
    )
```

Use a package-relative import when `__package__` is set and a local import when the file runs directly. Generate A and verify that `question-bank-a.json` has no diff.

- [ ] **Step 5: Add the B wrapper and generate its bank**

Create the matching B constants and wrapper:

```python
SOURCE = ROOT / "content" / "courses" / "collision-pi" / "question-source-b.json"
OUTPUT = ROOT / "content" / "courses" / "collision-pi" / "question-bank-b.json"

def build_bank() -> dict:
    return build_bank_from_paths(
        SOURCE,
        PUZZLE,
        section_id="B",
        title="碰撞与π · B板块客观题库",
    )
```

Run `python scripts/generate_collision_pi_b_questions.py` and inspect the generated count, node order, first/last question, and UTF-8 text.

- [ ] **Step 6: Make the formal bank Schema section-conditional**

Keep the shared question payload rules and change the root contract to accept only A or B. Use `if/then` branches:

```json
{
  "if": {"properties": {"section_id": {"const": "A"}}, "required": ["section_id"]},
  "then": {
    "properties": {
      "questions": {"minItems": 140, "maxItems": 140},
      "question_count_by_node": {"minProperties": 20, "maxProperties": 20}
    }
  }
}
```

Add the B branch with 168 questions and 22 quota properties. The shared `node_id` accepts `^[AB]`, while each branch constrains bank questions and quota property names to that section's exact assessed IDs. Extend `variant_axis` with the eight B axes from Task 2 without removing any A axis.

Add mutation tests showing that an A bank with 168 questions, a B bank with an A node, or a B bank missing one quota fails Draft 2020-12 validation.

- [ ] **Step 7: Run generator and schema verification**

```powershell
python scripts/generate_collision_pi_a_questions.py
python scripts/generate_collision_pi_b_questions.py
python -m unittest tests.test_question_bank tests.test_question_bank_b tests.test_question_source_b tests.test_project_contract -v
```

Validate `question-bank-a.json` and `question-bank-b.json` against `objective_question_bank.schema.json`. Expected: A remains 140 and byte-stable; B is 168; all focused tests and both schemas pass.

- [ ] **Step 8: Commit generation and bank artifacts**

```powershell
git add scripts/collision_pi_question_bank.py scripts/generate_collision_pi_a_questions.py scripts/generate_collision_pi_b_questions.py schemas/objective_question_bank.schema.json content/courses/collision-pi/question-bank-a.json content/courses/collision-pi/question-bank-b.json tests/test_question_bank.py tests/test_question_bank_b.py tests/test_project_contract.py
git commit -m "feat: generate collision pi B question bank"
```

---

### Task 4: Upgrade the Author Editor to Filter A and B

**Files:**
- Modify: `authoring/collision-pi-question-editor.template.html`
- Modify: `scripts/build_collision_pi_question_editor.py`
- Modify: `authoring/collision-pi-question-editor.html`
- Modify: `scripts/validate_question_editor.js`
- Modify: `tests/test_project_contract.py`

**Interfaces:**
- Consumes: checked-in A and B bank objects with ordered `question_count_by_node` maps.
- Produces: one generated editor containing `{A: bankA, B: bankB}`, a `questionSectionFilter`, section-aware node/scenario/type/keyword filters, and section-scoped local drafts.

- [ ] **Step 1: Make the static validator fail on the old one-bank editor**

Change the validator's data parsing expectation to:

```javascript
const banks = JSON.parse(scripts[0][1]);
if (banks.A.questions.length !== 140 || banks.B.questions.length !== 168) {
  throw new Error('expected A=140 and B=168 questions');
}
```

Require the template/editor to contain `id="questionSectionFilter"`, `section=B` URL handling, and a section-qualified draft key. Run:

```powershell
node scripts/validate_question_editor.js
```

Expected: FAIL because the current embedded data is a single A bank and no section control exists.

- [ ] **Step 2: Add a failing Python build-parity test**

Update `tests/test_project_contract.py`:

```python
def test_checked_in_question_editor_matches_builder(self):
    from scripts.build_collision_pi_question_editor import build
    expected = build()
    actual = (ROOT / "authoring/collision-pi-question-editor.html").read_text(encoding="utf-8")
    self.assertEqual(actual, expected)
```

Also parse the embedded JSON and assert its keys are exactly `{"A", "B"}` and counts are A=140/B=168.

- [ ] **Step 3: Embed both banks deterministically**

Replace the single `BANK` constant with:

```python
BANKS = {
    "A": ROOT / "content/courses/collision-pi/question-bank-a.json",
    "B": ROOT / "content/courses/collision-pi/question-bank-b.json",
}

def build() -> str:
    template = TEMPLATE.read_text(encoding="utf-8")
    payload = {
        section: json.loads(path.read_text(encoding="utf-8"))
        for section, path in BANKS.items()
    }
    data = json.dumps(payload, ensure_ascii=False, indent=2)
    if "__QUESTION_BANKS_JSON__" not in template:
        raise ValueError("question banks placeholder is missing")
    return template.replace("__QUESTION_BANKS_JSON__", data)
```

Rename the template placeholder from singular to plural and keep the embedded JSON as the first script block.

- [ ] **Step 4: Add the section selector and section state**

Place the section selector before the node selector:

```html
<label>板块
  <select id="questionSectionFilter">
    <option value="A">A 板块</option>
    <option value="B">B 板块</option>
  </select>
</label>
```

Initialize from `new URLSearchParams(location.search).get("section")`; accept only keys present in `banks`, otherwise use A. Define `currentBank()` and derive every question, quota, node option, scenario option, summary, navigation action, restore action, copy/export action, and save action from it.

- [ ] **Step 5: Scope drafts and reset invalid filters on section change**

Use:

```javascript
function draftKey(sectionId) {
  return `collision-pi-question-editor:${sectionId}:draft-v1`;
}
```

When the section changes: persist the outgoing section draft, load the incoming section draft, rebuild node/scenario controls, choose the first assessed node unless the URL supplies a valid node, reset type/scenario/keyword filters, and render. Never reuse a scenario ID or node ID absent from the new bank.

- [ ] **Step 6: Preserve combined filtering behavior**

For the active section, apply node, type, scenario, and normalized keyword predicates together. The `standalone` scenario option matches questions without `scenario_id`; a real scenario option matches exact `scenario_id`; empty results show `当前筛选条件下没有题目。`.

The summary must report the active bank only. Metadata display keeps `question_style`, `scenario_id`, and `event_stage`. Ensure long formulas and scenario IDs wrap on narrow screens.

- [ ] **Step 7: Rebuild and run static verification**

```powershell
python scripts/build_collision_pi_question_editor.py
node scripts/validate_question_editor.js
python -m unittest tests.test_project_contract -v
```

Expected: Node reports A=140, B=168, and two script blocks; Python build-parity passes.

- [ ] **Step 8: Run browser acceptance**

Serve the worktree root as UTF-8 and open:

```text
http://127.0.0.1:8765/authoring/collision-pi-question-editor.html?section=B&bank=3
```

Verify with browser controls:

- A shows 20 assessed nodes and 140 questions.
- B shows 22 assessed nodes and 168 questions.
- B4.2 has 12 questions; B5.4 has 4.
- Each question type returns a non-zero result.
- `SC-B4-SOLVE` returns 20; `SC-B5-CHAIN` returns 16.
- `standalone` hides every question with `scenario_id`.
- A nonexistent keyword produces the empty state.
- Switching B→A→B does not retain invalid nodes/scenarios and does preserve separate drafts.
- Console error count is zero.
- 1280 px and 375 px viewports have no horizontal overflow.

- [ ] **Step 9: Commit the dual-section editor**

```powershell
git add authoring/collision-pi-question-editor.template.html authoring/collision-pi-question-editor.html scripts/build_collision_pi_question_editor.py scripts/validate_question_editor.js tests/test_project_contract.py
git commit -m "feat: filter collision pi questions by section"
```

---

### Task 5: Update Project Facts and Complete End-to-End Verification

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/roadmap.md`
- Modify: `docs/decisions/conversation-decisions.md`
- Modify: `tests/test_project_contract.py`
- Modify: `tests/test_independence.py` only if a new runtime/config path requires independence coverage

**Interfaces:**
- Consumes: final node model, A/B sources, A/B banks, shared builders, and dual-section editor.
- Produces: current project facts, deterministic build evidence, full automated evidence, browser evidence, and a complete 168-prompt content review.

- [ ] **Step 1: Make current-doc tests require the new exact facts**

In `tests/test_project_contract.py`, require all four designated docs to contain these statements exactly:

```text
《碰撞与π》知识拼图共 136 个节点：A=27、B=27、C=46、D=36。
A 板块有 20 个承载题目的二级节点，共 140 道客观题。
B 板块有 22 个承载题目的二级节点，共 168 道客观题。
B 题库包含 15 个场景题组和 32 道计算题。
```

Keep negative assertions against `144 个节点`, `139 个节点`, `A=32`, `B=30`, `192 道`, and `每节点 6 道` when those phrases claim the current contract rather than historical context.

- [ ] **Step 2: Run the doc test and confirm RED**

```powershell
python -m unittest tests.test_project_contract -v
```

Expected: failures identify each current document that still states 139/B=30 or omits the B bank contract.

- [ ] **Step 3: Update the four current documents**

Change only current project facts and the B authoring milestone. Preserve the status-question separation, answer isolation, wrong-answer follow-up policy, video-primary/source-cross-check rule, and roadmap boundaries for student runtime, accounts, payment, and deployment.

- [ ] **Step 4: Run deterministic rebuilds twice**

Run this exact sequence twice:

```powershell
python scripts/build_collision_pi_knowledge_puzzle.py
python scripts/generate_collision_pi_a_questions.py
python scripts/generate_collision_pi_b_questions.py
python scripts/build_collision_pi_question_editor.py
```

Record SHA-256 for `knowledge-puzzle.md`, both bank JSON files, and the generated editor after each round. The two rounds must match exactly, and the worktree must contain no generated drift.

- [ ] **Step 5: Run the complete automated suite and all schemas**

```powershell
python -m unittest discover -s tests -v
node scripts/validate_question_editor.js
```

Validate these four data files with `Test-Json`:

```text
knowledge-puzzle.json → knowledge_puzzle.schema.json
question-source-a.json → objective_question_source.schema.json
question-source-b.json → objective_question_source_b.schema.json
question-bank-a.json and question-bank-b.json → objective_question_bank.schema.json
```

Expected: zero test failures; Node reports A=140/B=168; every Schema passes.

- [ ] **Step 6: Review all 168 B prompts and explanations**

Read every final rendered B prompt once. Inspect these slices in full:

- all B3 questions for correct equation conditions and signs;
- all B4 questions for algebra, physical-root selection, special ratios, and limit behavior;
- all B5 questions for event ordering, wall updates, terminal conditions, and count conventions;
- all 32 calculations against their independent fixtures;
- all multiple-choice answers after option rotation;
- every explanation for source-option-position wording.

Reject completion if any item requires a prior answer, hides a direction/system/time boundary needed for the answer, uses a conservation law outside its interval, treats momentum as a scalar, treats kinetic energy as directional, or presents a physically irrelevant distractor.

- [ ] **Step 7: Repeat browser acceptance on the final generated editor**

Reload the UTF-8-served editor after the final build and repeat every acceptance item from Task 4 Step 8. Confirm the summary, node order, scenario counts, standalone behavior, empty state, section switching, separate drafts, console, and both viewport widths.

- [ ] **Step 8: Check repository integrity and commit docs/guards**

```powershell
git diff --check
git status --short
git add AGENTS.md README.md docs/roadmap.md docs/decisions/conversation-decisions.md tests/test_project_contract.py tests/test_independence.py
git commit -m "docs: record the collision pi B question contract"
```

Do not add `tests/test_independence.py` if it has no intentional diff. After the commit, rerun the full Python suite, Node validator, and `git status --short --branch` before the final branch review.

---

## Final Verification Checklist

- [ ] B has exactly 5 stage nodes, 22 assessed nodes, and 27 total nodes in the approved order.
- [ ] Course totals are exactly A=27, B=27, C=46, D=36, total 136.
- [ ] B source and bank contain exactly 168 questions with exact per-node quotas.
- [ ] B style counts are scenario=104, calculation=32, concise=32.
- [ ] Fifteen scenario families and their node allocations match the spec.
- [ ] All 32 calculation fixtures independently satisfy their stated equations and event updates.
- [ ] A bank remains byte-stable at 140 questions and its accepted contracts stay green.
- [ ] Both checked-in banks equal their generator outputs; the checked-in editor equals its builder output.
- [ ] The editor switches A/B and applies node, type, scenario, standalone, and keyword filters without cross-section state leakage.
- [ ] Two complete rebuild rounds are byte-identical.
- [ ] Full Python, Node, and all formal Schema validations pass.
- [ ] Browser acceptance passes at desktop and mobile widths with zero console errors.
- [ ] Every B prompt and explanation has been read once; B3/B4/B5 and all calculations receive focused physics review.
- [ ] Current docs contain the exact 136-node and A/B bank facts and retain all product boundaries.
- [ ] `git diff --check` is clean and the final worktree has no uncommitted generated drift.
