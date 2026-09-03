# Task 3 Report — C visual question source

## Delivered files

- `content/courses/collision-pi/question-source-c.json`
  - 180 authored questions: 12 ordered scenarios / 108 scenario questions and 72 standalone questions.
  - Exact style distribution: scenario 108, calculation 24, concise 48.
  - Exact presentation distribution: text_only 60, stem_figure 72, option_figures 24, figure_sequence 24.
  - Exact type distribution: single_choice 108, multiple_choice 48, multi_blank 24.
  - Uses only the 36 Task 1/2 manifest diagram IDs, with 24 unique four-image option sets and 24 ordered figure sequences.
  - Includes six authoritative source records, 24 independently checkable calculation fixtures, scenario author notes, C1–C8 core scope, and C9 elective scope.
- `schemas/objective_question_source_c.schema.json`
  - Draft 2020-12 closed schema with exact root identity, quota, source, fixture, scenario, and standalone collection contracts.
  - Routes scenario `ask` versus standalone `prompt`; routes choice/multiple-choice/multi-blank payloads; restricts the four presentation modes; requires a fixture for calculations; and restricts C9 to elective scope.
- `tests/test_question_source_c.py`
  - Exact quota / scenario / style / type / presentation tests; three 66/66/48 checkpoints; image routing checks; wording guards; unique-final-prompt guard; source scope checks; and independent calculation-fixture recomputation.

## TDD evidence

RED:

```text
python -m unittest tests.test_question_source_c -v
Ran 14 tests ... FAILED (failures=14)
```

Those failures explicitly reported the missing C schema and source artifacts. A later focused RED for the non-duplication contract reported `180 != 139`, proving that the added guard caught repeated final prompts before the one-shot authoring pass revised them.

GREEN:

```text
python -m unittest tests.test_question_source_c -v
Ran 15 tests ... OK
```

Checkpoint commands each passed after the final authored source:

```text
test_c1_c3_checkpoint ... OK  (66 questions)
test_c4_c6_checkpoint ... OK  (66 questions)
test_c7_c9_checkpoint ... OK  (48 questions)
```

## Schema and suite evidence

```text
Test-Json -Json question-source-c.json -SchemaFile objective_question_source_c.schema.json
C source schema valid

python -m unittest discover -s tests -v
Ran 129 tests ... OK
```

## Self-review

Reviewed all 180 entries through the source contracts and a record-level audit:

- 180 non-empty prompts/asks and explanations; all `(node_id, key)` pairs unique; final prompts unique after the duplicate guard.
- All 24 calculation questions reference exactly one node-matching fixture; the test independently recomputes raw coordinates, ellipse axes, weighted transforms, energy circles, momentum lines, both line-circle roots, wall reflections, every state-chain transition, safety-sector inequality, `theta`, `2theta`, and count steps.
- All C7 prompts name the relevant `theta` / `2theta` / angle distinction; the ambiguity guard found zero matches.
- All C9 questions are `elective` (12); C1–C8 are `core` (168). C9 wording distinguishes folded position-space reflections from unfolded straight rays.
- No forbidden graph-confusion wording was found. Distractors avoid answer order, colour, typography, identifiers, and other non-physical cues.
- All 120 graphical questions carry valid existing IDs, a non-empty focus, and comply with their routing mode. Every C1–C8 secondary node has at least two graphical questions.

## Concerns

None. The task deliberately leaves the formal C question-bank expansion to Task 4; this source contains author-only answers and fixtures and does not change student delivery behavior.

---

# Fix round 1/5 — content-correctness repair

## Files changed

- `content/courses/collision-pi/question-source-c.json`
  - Re-audited all 180 records. All 156 choice records now carry an author-side `answer_contract`; its expected answer text is checked separately from the rendered `correct` flags. All 24 calculation records remain tied to independently recomputed fixtures.
  - Rewrote all 48 multiple-choice option sets so that both keyed statements follow directly from the displayed quantities, formulas, and explanation. This fixes the identified coordinate, mass-ratio, energy, momentum-line, and `1/2 -> 1/4` contradictions.
  - Reworked all 24 `option_figures` questions into single-answer, mutually exclusive figure-caption identification tasks. A candidate image can still depict a true fact, but it cannot become a second answer to the stated task.
  - Repaired the 24 figure sequences to the declared stage derivations: initial/axes/state boundary; equal-mass/ratio-4/ratio-16 ellipses; scaling progression; chord progression; wall progression; chain/safe-sector progression; chord/step/count; integrated legend; and folded/unfolded wedge progression.
  - Made every calculation prompt expose all fixture inputs. In particular wall prompts show the initial `(x,y)`, state-chain prompts list each event in order, and C9.2 now supplies both masses and original positions before requesting `Q=(6,2)`.
  - Removed every `本题额外聚焦…` suffix and the replacement wrapper text. Repeated questions were recast with node-specific physical operations (e.g., sign-to-direction translation, coefficient expansion, or separate slope/intercept comparison).
  - Added explicit C7.2 questions distinguishing `弦方向角alpha` from `圆周角`, `圆心角`, `theta`, and one-update `2theta`.
- `schemas/objective_question_source_c.schema.json`
  - Adds a closed `answerContract` definition. Choice payloads require a contract with expected option text and a stated basis; figure-caption contracts additionally require their target manifest ID.
- `tests/test_question_source_c.py`
  - Expanded from 15 to 22 source tests. New guards cover normalized near-duplicate stems, all 156 choice contracts and per-option key mutations, 24 mutually exclusive figure-caption tasks, semantic sequence order, every state-chain event order, all calculation input visibility, and C7.2 angle-role coverage.

## TDD evidence

RED (before the repair):

```text
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_choice_answers_have_auditable_contract_for_every_record tests.test_question_source_c.QuestionSourceCTests.test_normalized_prompts_are_substantively_distinct tests.test_question_source_c.QuestionSourceCTests.test_figure_sequences_follow_declared_derivations tests.test_question_source_c.QuestionSourceCTests.test_calculation_prompts_list_each_state_chain_event tests.test_question_source_c.QuestionSourceCTests.test_c7_2_names_chord_direction_angle_and_distinguishes_angle_roles -v

Ran 5 tests: 1 error, 4 failures
- `answer_contract` missing from choice entries
- stock duplicate suffix still present
- C1 figure sequence was `initial, terminal, quadrants` rather than the declared derivation
- a state-chain prompt said only “given two events” without their order
- C7.2 had no `弦方向角`
```

GREEN:

```text
python -m unittest tests.test_question_source_c -v
Ran 22 tests ... OK
```

The intermediate input-visibility guard first correctly rejected a numerical `pi` fixture that was rendered to students as the equivalent symbolic `span=pi`; the guard now accepts that explicit symbolic form and the focused suite is green.

## Checkpoints and Schema

```text
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_c1_c3_checkpoint tests.test_question_source_c.QuestionSourceCTests.test_c4_c6_checkpoint tests.test_question_source_c.QuestionSourceCTests.test_c7_c9_checkpoint -v
Ran 3 tests ... OK
- C1–C3: 66 records
- C4–C6: 66 records
- C7–C9: 48 records

Test-Json -SchemaFile schemas/objective_question_source_c.schema.json
Schema valid
```

## Fresh record-level audit

- Reviewed each of the 48 rewritten multiple-choice records against its displayed stem and explanation; their two keyed claims are now direct consequences of the displayed data or formula. The source test independently detects any changed flag against each contract, for every option in all 156 choice records.
- Reviewed the 108 single-choice records: figure options now use unique caption targets; text/figure claims were checked against their stated coordinates, mass ratios, energy equations, reflection rule, sequence, or wedge definition.
- Recomputed all 24 calculation answers through the test oracle and confirmed every visible prompt has the required fixture data. The state-chain calculation prompts explicitly list 2 and 6 events respectively.
- Reviewed all 24 `option_figures` records and all 24 `figure_sequence` records individually. Figure IDs are existing manifest IDs only; sequences match the stage-specific derivation table; all option-figure records have exactly one target caption and one correct flag.
- Checked wording for stock suffixes, dependent-question references, and the quoted defective patterns. The former stock suffix/wrapper text is absent; the remaining valid `E=9` statement is the corrected consequence of `x^2+y^2=18`, not an `E=8` item.

## Full suite and concerns

```text
python -m unittest discover -s tests -v
Ran 136 tests in 17.387s ... OK
```

No content blocker remains. The caption-based option-figure format intentionally tests precise visual-model identification rather than asserting that the other physically valid diagrams are false.

## Repair commit

`4b724f6 fix: repair collision pi C question contracts`

---

# Fix round 2/5 — physical step model and visual-contract repair

## Root cause and changes

- The prior C7 wording conflated a single physical collision with a `2theta` advance. The correct model is: a block collision and the following wall reflection form one event pair; unfolding that pair advances the angle by `2theta`. Thus for `M/m=4`, `floor(pi/(2theta))=3` event pairs correspond to six physical collisions, matching `CAL-C6-CHAIN-02` and the Task 1 terminal state chain.
- Both C7 angle-count fixtures now expose `pair_steps` and `physical_collisions`; their calculation prompts request both quantities. The independent fixture oracle recomputes them and cross-checks the six C6 events.
- All 48 multiple-choice prompts have exactly one selection instruction. Their normalized prompt + correct-claim + explanation fingerprint is guarded against duplicates.
- All 156 choices use `structured_claims` contracts with stable option IDs `A`–`D`; the former copied `expected_option_texts` and prose `basis` fields are removed. Option-figure contracts use a manifest/diagram-source predicate of template, coordinate system, parameters, and labels.
- All 24 option-figure stems now state observable physics/geometry criteria and use neutral labels `图A`–`图D`. They do not disclose a target caption or diagram ID. The test resolves the predicate against `diagram-source-c.json` and requires exactly one matching candidate.
- The C schema now requires option IDs and closed structured contracts. Duplicate `answer_contract` entries in conditional required arrays were deduplicated.

## TDD evidence

RED:

```text
python -m unittest ...test_choice_contracts_are_structured... ...test_multi_choice_prompts_are_distinct... ...test_option_figure_stems_do_not_leak... ...test_c7_pair_steps_map_to_two_physical_collisions ...test_schema_required_lists_have_no_duplicates -v

Ran 5 tests: 4 failures, 1 error
- legacy figure-caption/text-copy contracts present
- multi-choice prompts contained four repeated selection instructions
- option figures leaked captions and had no physical predicate
- C7 count fixture lacked pair_steps
- Schema branch had seven required entries but only two unique fields
```

GREEN:

```text
python -m unittest tests.test_question_source_c -v
Ran 26 tests in 1.800s ... OK
```

## Verification

```text
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_c1_c3_checkpoint tests.test_question_source_c.QuestionSourceCTests.test_c4_c6_checkpoint tests.test_question_source_c.QuestionSourceCTests.test_c7_c9_checkpoint -v
Ran 3 tests ... OK (66 / 66 / 48)

Test-Json -SchemaFile schemas/objective_question_source_c.schema.json
Schema valid

python -m unittest discover -s tests -v
Ran 140 tests in 17.037s ... OK
```

## Fresh audit and concerns

- Re-audited every C7 record, all 48 multiple-choice prompts/options/contracts, all 24 option-figure records, and all 156 structured choice contracts.
- No target caption or diagram ID remains in an option-figure stem or explanation; each predicate selects exactly one of its four existing manifest diagrams.
- No blocker remains.

## Repair commit

`cc0d527 fix: model C collision event pairs`

---

# Fix round 2/5 continuation — independently evaluable typed claims

## Scope closed

- Replaced every deprecated boolean `physics.predicate` in the 132 text/stem-figure choice records with a closed `claim: {kind, parameters}` payload. Each of the 156 answer flags is now recomputed by the C-source test from physical quantities or, for visual options, from `diagram-source-c.json`; no claim stores an expected-truth or correctness boolean.
- The displayed text of all 132 text/stem-figure option records is rendered by the same canonical typed-claim renderer that the test evaluates. The test rejects any drift between rendered claim text and stored option text.
- The actual claim families are covered across C1–C9: velocity state/direction/quadrant; raw energy ellipse and axes; mass-weighted point and energy circle; momentum slope/parallel/intersection; wall reflection/radius; event count/safe sector; angle step/event-pair/collision count; legend mapping; and folded/unfolded wedge relations.
- All 24 `option_figures` records now carry `diagram_matches_query` typed candidates. The query is independently applied to each source diagram’s template, coordinate system, parameters, and labels. Figure stems retain neutral 图A–图D labels and do not reveal captions or IDs.
- The option-figure label is likewise canonical: the test derives `图<claim.option_id>` and rejects stored-label drift.
- Added mutation evidence: changing a velocity, a mass in a weighted coordinate, an angle-count mass ratio, or a candidate diagram template changes the evaluator result. The contracts cannot pass by merely flipping stored option flags.
- Tightened the C schema so each answer-contract claim requires `option_id`, `family`, and `claim`; the typed claim itself is a closed `{kind, parameters}` object. The former `predicate` object is not accepted.

## TDD evidence

RED, before source migration:

```text
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_choice_contracts_are_structured_and_do_not_repeat_author_answer_text -v
FAIL: c1-1-scenario-03 retained predicate instead of typed claim
```

The first post-migration focused run also caught duplicate normalized prompts, an x-axis wording issue, and duplicate C7 angle distractors; these were corrected by node-specific physical focuses, explicit coordinate wording, and distinct numerical angle claims.

GREEN:

```text
python -m unittest tests.test_question_source_c -v
Ran 26 tests in 1.786s ... OK
```

## Checkpoints, schema, full suite

```text
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_c1_c3_checkpoint tests.test_question_source_c.QuestionSourceCTests.test_c4_c6_checkpoint tests.test_question_source_c.QuestionSourceCTests.test_c7_c9_checkpoint -v
Ran 3 tests ... OK (66 / 66 / 48)

Test-Json -SchemaFile schemas/objective_question_source_c.schema.json
C source schema valid

python -m unittest discover -s tests -v
Ran 140 tests in 17.247s ... OK
```

## Fresh record-level audit

- Re-evaluated all 156 option claims and matched the computed truth vector to all stored correct flags; each text option also equals its canonical typed rendering.
- Checked all 24 option-figure candidates against the authoritative diagram-source properties; exactly one candidate matches each query, and mutation rejects a changed candidate.
- Rechecked all 48 multiple-choice prompts for one selection instruction, two computed true claims, and normalized semantic uniqueness. Existing quota, scenario, presentation, sequence, fixture, C7 pair-step, and C9 folded/unfolded tests remain green.

## Concerns

None. This closes the prior self-identified circular boolean-contract gap without changing A/B assets, generators, SVGs, manifest, or diagram source.

---

# Fix round 3/5 — generalized counts, geometry, and anonymous option accessibility

## Root causes and repairs

- The former C7 evaluator used `floor(pi/(2theta))*2`, which is valid only when all collisions form full block-plus-wall pairs. It discarded the odd residual collision for `M/m=9`. The canonical `N=ceil(pi/theta)-1` oracle now drives C7 typed claims and fixtures; each count claim explicitly exposes full pairs, residual physical collisions, and total physical collisions. The nine M/m=9 records now key `4` pairs, `1` residual, and `9` total collisions, while the M/m=4 six-event chain remains correct.
- “弦方向角是theta” was a reference-axis conflation. C7 now states the standard reference explicitly: for slope `-sqrt(M/m)`, the direction angle measured from `+x` is `(theta-pi/2) mod pi`. A new geometrically evaluated `chord_direction_angle` claim replaces the prior misleading option; explanations retain the distinct `2theta` event-pair advance.
- The SVGs and manifest keep their meaningful standalone captions/alt text. For anonymous option use, each of the 24 source contracts now supplies the only student-visible accessibility payload `{A: 图A, …, D: 图D}`. The C schema requires it for `option_figures`; tests reject source captions/alt text in the prompt or option-context exposure.
- Legend claims now point to `cp-c-element-legend-overview` and resolve `circle`, `line`, `chord`, and `mirror` from authoritative `diagram-source-c.json` labels. They no longer embed an author-side mapping beside the asserted answer.
- Typed claims now have a closed permitted parameter-name surface, boolean parameter values are schema-rejected, and tests enforce the exact parameter set for all 624 claims. Schema mutations for a hidden expected field and a boolean assertion both fail.
- All 48 multiple-choice prompts were re-audited with a detector that removes node/stage wrappers and checks the remaining physical relation, correct claim kinds, and explanation semantics. Each now states a distinct physical operation rather than relying on phase labels.
- `c7-3-calculation-22` and `c7-4-calculation-23` now have exactly four unique blanks (`theta`, `step`, `pair_steps`, `physical_collisions`); blank and accepted-answer arrays use `uniqueItems`, and all 24 calculations are checked for unique requested outputs.

## TDD evidence

RED:

```text
python -m unittest ...test_c7_collision_oracle_keeps_odd_residual_collision ...test_c7_chord_direction_angle_is_geometric_not_theta ...test_option_figures_expose_only_neutral_accessibility_labels ...test_calculation_blanks_are_unique_and_match_requested_outputs -v
FAIL/ERROR
- M/m=9 was keyed as 8 rather than 9
- no chord_direction_angle typed claim existed
- option_accessibility was absent
- C7 calculation blanks repeated pair_steps / physical_collisions
```

GREEN:

```text
python -m unittest tests.test_question_source_c -v
Ran 31 tests in 12.170s ... OK
```

Additional focused mutations verify M/m=4 -> 6, M/m=9 -> 9, and non-perfect-square M/m=10 -> 10; a changed mass, velocity, angle, diagram candidate, hidden boolean, or hidden expected field changes/rejects the contract.

## Verification

```text
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_c1_c3_checkpoint tests.test_question_source_c.QuestionSourceCTests.test_c4_c6_checkpoint tests.test_question_source_c.QuestionSourceCTests.test_c7_c9_checkpoint -v
Ran 3 tests ... OK (66 / 66 / 48)

Test-Json -SchemaFile schemas/objective_question_source_c.schema.json
C source schema valid

python -m unittest discover -s tests -v
Ran 145 tests in 19.144s ... OK
```

## Fresh audit

- Reviewed all affected C7 records, including the nine M/m=9 questions, every C7 explanation, and both C7 calculation prompts; the ceiling formula, odd residual, and +x chord reference are consistent.
- Reviewed all 48 multiple-choice records with the wrapper-stripping physical-semantic guard, all 24 option-figure anonymous accessibility exposures, all 24 calculations’ unique blank IDs, and all 624 typed claims’ exact parameter shape and recomputed truth.
- A/B source, diagrams, manifest, and generator behavior remain untouched; C diagram determinism remains green in the full suite.

## Concerns

None.

## Fix round 5

Implemented the final anonymous-option seam: the generator emits the same
`option_accessibility_label` property named by `accessible_name_source`, and
the embedded figure is explicitly aria-hidden.  The formal schema now requires
the option-figure rendering contract and all four neutral labels; destructive
mutations removing the rendering object, figure ref, label, hidden flag, or
declared source fail validation.  A/B remain valid and mutations to C-only
`calculation` / `elective_method` values fail formal validation.

Corrected active stem-figure mass-ratio conflicts for momentum and equal-angle
items, and rewrote the reviewed C1/C4/C7 pairs so their correct claim kinds and
asked relations differ (coordinate reading versus quadrant, slope versus
origin, count versus 2theta step).  C7 angle values use the standard +x chord
direction and the ceiling collision oracle.

```text
RED: option accessibility test failed with the former mismatched field name.
GREEN: python -m unittest tests.test_question_source_c -q
Ran 34 tests in 17.640s ... OK

Test-Json objective_question_source_c.schema.json ... True
A/B formal schema checks ... True / True
```

Concern: the full `unittest discover` run was started but its final aggregate
line was not captured before this continuation ended; focused C tests and
schema checks above are current evidence.

## Fix round 5 continuation

Focused C source suite was rerun after restoring the interruption state and
repairing the four active-figure mass conflicts (`c4-2-scenario-04`,
`c4-3-scenario-03`, `c7-2-scenario-04`, `c7-3-scenario-03`).  Their typed
claims, rendered options, and flags were recomputed together from the same
physics contracts.

```text
python -m unittest tests.test_question_source_c -q
Ran 34 tests in 17.449s ... OK

python -m unittest discover -s tests -v
exit code 0 (all displayed tests passed; tool output was truncated)
```

---

# Fix round 4/5 — consumable anonymous figures and closed claim branches

## Repairs

- Extended `scripts/collision_pi_question_bank.py` only for C payloads: visual presentation metadata, figure references, and diagram focus survive expansion. Each option-figure output retains its figure reference but carries `accessibility_label: 图A–图D`, `embedded_figure_aria_hidden: true`, and a question-level `anonymous_option_rendering` contract whose accessible-name source is the separate neutral label. A/B source lacks C presentation metadata, so their generated bytes remain unchanged.
- Extended the formal bank schema to support C’s 180-node contract and its C event/variant vocabulary. The C expansion now validates through the consumable formal schema.
- Replaced global typed-claim parameter permissiveness with 21 discriminated per-kind parameter schemas. Each has exact required fields, `additionalProperties: false`, typed nested vectors, and a closed semantic event object. `event_count` now requires an alternating block/wall identity/order, not merely a list length.
- Added adversarial schema/evaluator checks for nested hidden truth fields, nested booleans, wrong-kind parameters, missing required fields, malformed event objects, and a valid-but-order-swapped event list that the evaluator rejects.
- Materially separated all seven reviewed multiple-choice pairs by changing their physical state/mass-ratio givens and canonical claims/options. The new signature removes headings, phases, and focus copy while retaining normalized physical givens, full claims, answer flags, and explanation; a cosmetic focus-only mutation demonstrably still collides.
- Removed every doubled `弦方向角以+x轴为参照` prompt occurrence.

## TDD evidence

RED:

```text
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_expansion_keeps_c_visual_contract_and_anonymizes_option_figures -v
FAIL: expanded C questions had no presentation_mode / anonymous option contract
```

GREEN:

```text
python -m unittest tests.test_question_source_c -v
Ran 33 tests in 14.514s ... OK

python -m unittest tests.test_question_bank.QuestionBankTests.test_a_wrapper_preserves_checked_in_bank_bytes tests.test_question_bank_b.QuestionBankBTests.test_checked_in_b_bank_matches_generator -v
Ran 2 tests ... OK
```

## Verification and audits

```text
Three C checkpoints: 3 tests ... OK (66 / 66 / 48)
Test-Json C source schema: valid

Non-C project suite: 38 tests in 1.781s ... OK
A/B banks and sources: 76 tests in 16.248s ... OK
C source/generator suite: 33 tests in 14.514s ... OK
Total: 147 tests ... OK
```

- Audited all 24 expanded option-figure records: all retain their required figure refs; the only exposed option name is 图A–图D; raw SVG caption/alt text is absent from the option context; embedded artwork must be `aria-hidden`.
- Audited all 624 typed claims with exact per-kind parameter shapes; all 48 multi-choice records, seven reviewed pairs, 24 calculations, and C7 prompts are covered by the strengthened source tests.

## Concerns

None.
