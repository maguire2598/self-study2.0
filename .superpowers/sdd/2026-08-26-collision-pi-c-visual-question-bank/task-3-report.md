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

---

# Fix round 6 — exhaustive stem compatibility, distinct relations, and manifest validation

## Root causes and repairs

- The four `conceptual_reference` checks introduced in round 5 were the only records whose physical facts were validated; the other 68 records bypassed all numerical comparison. The validator now ignores the role label and classifies every one of the 72 stem figures by template-specific fact dimensions. It checks every applicable mass ratio, coordinate system, visible energy equation, wall-reflection point, state-chain event sequence, safe-sector boundary, momentum geometry, equal-angle relation, and wedge angle against `diagram-source-c.json`.
- All 24 previously mismatched stem records were reconciled with the authoritative diagram source. The two reviewed 9:1 momentum questions retain `M/m=9/1`, use the existing 9:1 weighted-state figure as the stated mass source, and independently recompute the zero-momentum slope as `-3`. Other energy, scale, angle, and wedge records now use the mass/energy values represented by their figures. The C9 calculation fixture and displayed answer were recomputed for its 4:1 wedge.
- `c4-2-scenario-04` now assesses chord-endpoint invariants: its two states have zero difference in both the weighted momentum expression and radius squared, explicitly separating a collision chord from a continuous circular trajectory. A new `chord_state_invariants` typed claim independently recomputes both differences. `c7-2-scenario-04` now keys the `2theta` event-pair step plus the standard chord direction, instead of repeating the collision-count relation.
- The duplicate guard now fingerprints claim kinds and truth positions while ignoring all numeric values and focus/explanation prose. All seven formerly reviewed pairs differ under this relation-only signature; adversarial number-only and focus/explanation-only mutations still collide.
- C generation now resolves every source question and option figure reference through the checked-in 36-entry manifest before expansion. Both source and formal schemas carry the exact manifest ID enum, and mutations of either route to `not-a-manifest-diagram` fail source validation, generation, and formal bank validation.

## TDD evidence

RED before implementation:

```text
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_ratio_nine_momentum_questions_key_negative_three_slope tests.test_question_source_c.QuestionSourceCTests.test_every_stem_figure_declares_and_meets_its_compatibility_role tests.test_question_source_c.QuestionSourceCTests.test_reviewed_pairs_differ_in_assessed_relation_not_only_numbers_or_focus tests.test_question_source_c.QuestionSourceCTests.test_generation_and_formal_schema_reject_non_manifest_figure_references -v

Ran 4 tests in 1.216s
FAILED (failures=3, errors=1)
- both 9:1 momentum records still keyed -4/-2
- c2-1-scenario-04 was the first of 24 mass/figure contradictions
- c4-2-scenario-02 and -04 had the same assessed-relation signature
- the actual generator had no manifest-validation entry point
```

GREEN after implementation:

```text
python -m unittest tests.test_question_source_c -v
Ran 38 tests in 19.353s ... OK

python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_c1_c3_checkpoint tests.test_question_source_c.QuestionSourceCTests.test_c4_c6_checkpoint tests.test_question_source_c.QuestionSourceCTests.test_c7_c9_checkpoint -v
Ran 3 tests in 0.013s ... OK (66 / 66 / 48)

Test-Json -SchemaFile schemas/objective_question_source_c.schema.json
C source schema valid
```

## Independent audits and full verification

- All 180 records were rechecked through the keyed-answer oracles: 156 choice records recompute every typed claim and compare the truth vector to flags; all 24 calculations recompute accepted answers from fixtures.
- All 72 stem figures pass the role-independent, dimension-classified compatibility validator. Its adversarial mutations cover mass ratio, velocity/position coordinate systems, momentum geometry, state sequence, safe-sector boundary, equal-angle mass ratio, and wedge geometry.
- All 24 option-figure questions still resolve exactly one anonymous, neutral candidate from the diagram source; accessibility labels and `aria-hidden` behavior remain unchanged.
- All seven former duplicate pairs pass the relation-only audit, including explicit number-only and focus/explanation-only collision tests.

```text
python -m unittest tests.test_question_bank.QuestionBankTests.test_a_wrapper_preserves_checked_in_bank_bytes tests.test_question_bank_b.QuestionBankBTests.test_checked_in_b_bank_matches_generator tests.test_collision_pi_c_diagrams.CollisionPiCDiagramTests.test_build_is_deterministic -v
Ran 3 tests in 0.016s ... OK

Generated C bank + Test-Json -SchemaFile schemas/objective_question_bank.schema.json
formal C bank schema valid

python -m unittest discover -s tests -q
Ran 152 tests in 34.395s ... OK
```

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

## Final round-5 consistency audit

- Added closed source-side `figure_role` declarations to every one of the 72
  `stem_figure` records.  `active_physics` is reserved for the four diagrams
  whose numerical mass/coordinate/geometry facts are student-active;
  `conceptual_reference` is explicit for the remaining conceptual diagrams.
- The deterministic validator resolves all 72 references through
  `diagram-source-c.json`.  Active records compare visible mass ratio,
  coordinate representation, structured mass parameters, momentum-chord
  geometry, and equal-angle declarations.  It includes mass-ratio,
  coordinate-system, momentum-diagram, and equal-angle-ratio adversarial
  mutations.
- Rechecked the four reviewer-cited records: c4-2-scenario-04,
  c4-3-scenario-03, c7-2-scenario-04, c7-3-scenario-03.

```text
python -m unittest tests.test_question_source_c -q
Ran 35 tests in 17.480s ... OK

python -m unittest tests.test_question_bank.QuestionBankTests.test_a_wrapper_preserves_checked_in_bank_bytes tests.test_question_bank_b.QuestionBankBTests.test_checked_in_b_bank_matches_generator tests.test_collision_pi_c_diagrams.CollisionPiCDiagramTests.test_build_is_deterministic -v
Ran 3 tests in 0.016s ... OK

Test-Json C source schema ... True
python -m unittest discover -s tests -v
Ran 149 tests in 34.452s ... OK
```

## Final concerns

None.

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

---

# Fix round 7 — mass-weighted safe sectors and nonzero momentum figures

## Repairs

- Recomputed every C safe-sector statement from `y=sqrt(m/M)x`, not merely the eight reviewer-cited stem figures. The 16:1 state-chain records now use `y=0.25x`; every 4:1 record uses `y=0.5x`. All 18 safe-sector questions carry the mass pair inside each typed claim, so the evaluator derives the boundary independently instead of trusting an author-entered slope.
- Reconciled the six reviewer-cited momentum stems with `diagram-source-c.json`: ratio-4 and ratio-16 chords state `P=4`, while the parallel-line figure states both `P=2` and `P=4`. The two formerly correct zero-origin claims were replaced by independently recomputed chord-invariant claims using the visible endpoints.
- Removed the template/role bypass from stem compatibility. Safe-sector facts are checked even on a `state_chain` figure; momentum values, origin wording, correct chord endpoints, mass ratios, slopes, and line families are checked from the facts that appear in the stem and contract.
- Added adversarial regressions for a jointly mutated `y=999x` stem/contract, retained boundary after a mass mutation, `P=999` in the stem, `[999]` in diagram-source momentum values, `P=0` on a nonzero line, and a nonzero line claimed through the origin.

## TDD evidence

RED before implementation:

```text
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_every_stem_figure_declares_and_meets_its_compatibility_role tests.test_question_source_c.QuestionSourceCTests.test_all_safe_sector_statements_use_the_mass_weighted_boundary tests.test_question_source_c.QuestionSourceCTests.test_all_momentum_stem_figures_match_visible_nonzero_lines -v

Ran 3 tests in 0.020s
FAILED (failures=3)
- state-chain template accepted the jointly mutated safe boundary
- c6-2-scenario-01 still used y=x for M/m=16/1
- c4-2-scenario-03 stated P=0 while its figure carried P=4
```

GREEN after implementation:

```text
python -m unittest tests.test_question_source_c -q
Ran 40 tests in 21.113s ... OK

Get-Content question-source-c.json | Test-Json -SchemaFile objective_question_source_c.schema.json
C_SOURCE_SCHEMA=True

python -m unittest discover -s tests -q
Ran 154 tests in 32.743s ... OK
```

## Checkpoints and compatibility

```text
Three C checkpoints: 3 tests ... OK (66 / 66 / 48)
C formal-bank expansion and schema: 1 test ... OK (180 questions)
A byte parity, B generator parity, A/B formal strictness, C diagram determinism: 4 tests ... OK
```

Fresh independent audit output:

```text
AUDIT total=180 answer_contract_claims=624 calculations=24
AUDIT safe_sector_questions=18 all_ratio_boundaries_recomputed=True
AUDIT momentum_stem_figures=7 P_slope_origin_chord_checks=True
AUDIT stem_figures=72 all_applicable_dimensions_valid=True
```

## Concerns

None.

---

# Fix round 10 — closed structured visible-physics facts

## Repairs

- Replaced correctness-by-Chinese-regex for the affected C questions with a closed
  `visible_physics_contract`. Its typed facts cover `mass_ratio`,
  `safe_sector_boundary`, `momentum_value_set`, and `origin_relation`; every fact
  has a unique placeholder that occurs exactly once across the full prompt and
  explanation templates.
- Added one deterministic renderer and a production validator. The checked-in
  prompt/explanation must exactly equal canonical reconstruction, so punctuation,
  synonyms, appended assertions, missing slots, duplicate slots, unknown kinds,
  extra fields, hidden booleans, and coordinated diagram-source drift fail without
  extending a synonym parser.
- Bound all 18 safe-sector questions to their visible masses, derived
  `sqrt(m/M)` boundary, both equation/interval renderings, and all typed answer
  claims. Bound all 19 numeric-momentum records to structured value facts and
  typed origin relations. Bound all seven momentum stem figures directly to
  `diagram-source-c.json` momentum values; the seventh figure has an explicit
  diagram binding even though its prose does not state a numeric P.
- Carried the same reconstructible contract into formal expanded C questions,
  with scenario context included in the formal prompt template. Added recursively
  closed source/formal schemas. A/B expansion paths remain untouched.
- Removed the mass-ratio, momentum-equality, and origin-substring parsers from
  correctness checks. Compatibility and audit tests now consume structured facts
  and canonical reconstruction.

## TDD evidence

RED — production API absent:

```text
test_visible_physics_contract_api_exists ... FAIL
AssertionError: False is not true : production validator is missing
```

RED — affected records had no contracts:

```text
test_structured_visible_physics_contracts_round_trip_every_affected_record ... FAIL
AssertionError: 'visible_physics_contract' not found ... c4-2-concise-05
```

RED — formal expansion dropped the contract:

```text
test_expanded_bank_carries_reconstructible_visible_physics_contracts ... FAIL
AssertionError: 0 != 38
```

RED — malformed typed values were accepted by the renderer:

```text
test_canonical_visible_physics_rejects_text_and_fact_drift ... FAIL
AssertionError: ValueError not raised
```

GREEN:

```text
python -m unittest tests.test_question_source_c -q
Ran 48 tests in 21.686s ... OK

python -m unittest discover -s tests -q
Ran 162 tests in 33.321s ... OK
```

## Verification and fresh audit

```text
Three C checkpoints, source/formal schema, A byte parity, B generator parity,
and C diagram determinism: 8 tests in 10.407s ... OK

C_SOURCE_SCHEMA=True
A bank blob unchanged: 99a12906c97493be65038357065a017183bbde85
B bank blob unchanged: 3afb76fd3850d5530c90f72d90c9f8a19edc5803

AUDIT total=180 safe=18 numeric_momentum=19 momentum_stem_figures=7
AUDIT stem_figures=72 structured_claims=624 canonical_contracts=38
```

The adversarial suite appends and replaces all round-9 bypass families (ASCII,
full-width, presentation-form colons/equality, Chinese ratio wording, four total-
momentum phrasings, positive/negative/double-negative origin variants). It also
mutates structured masses, boundary coefficients, momentum values, diagram
bindings, origin enums, text, slots, kinds, and properties independently.

## Concerns

None.

---

# Fix round 8 — visible safe-sector masses and complete momentum-statement validation

## Repairs

- Added a question-level safe-sector validator that parses exactly one authoritative
  student-visible `(M, m)` pair from the stem/context, accepts spaced and decimal-equivalent
  notation, and binds every typed `safe_sector` claim to those exact masses and to
  `sqrt(m/M)`. Missing or ambiguous visible ratios fail. This applies to all 18 safe-sector
  questions: 9 `stem_figure`, 4 `text_only`, and 5 `figure_sequence` records (36 claims).
- Added one parser for numeric total-momentum statements in both symbolic and natural-language
  forms (`P=4`, `P = 4`, `总动量为4`, `总动量为 4`, Chinese punctuation, and units).
  Stem-figure compatibility now checks both the question stem and explanation against the
  referenced diagram-source momentum values, while preserving the valid phrase “不通过原点”.
- Audited all 19 records carrying numeric P statements in their stem or explanation. All seven
  direct momentum stem figures are tied to diagram-source values; the remaining calculation,
  text, and sequence records are checked for stem/explanation consistency.

## TDD evidence

RED before implementation:

```text
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_safe_sector_contract_masses_are_bound_to_the_visible_ratio tests.test_question_source_c.QuestionSourceCTests.test_momentum_statements_in_stem_and_explanation_match_the_figure -v

Ran 2 tests in 0.015s
FAILED (failures=1, errors=1)
- safe-sector validation had no question-level visible-mass binding
- c4-2-scenario-02 with `图示总动量为999` was incorrectly accepted
```

GREEN after implementation:

```text
Ran 2 tests in 0.014s
OK
```

The safe-sector test includes the exact reviewed mutation: both hidden `mass_large` values in
`c6-2-scenario-05` change from 4 to 16 while the visible stem remains 4/1. It also mutates
`mass_small`, only the visible ratio, missing/ambiguous ratios, and verifies spaced decimal
notation. The momentum test includes both exact reviewed mutations (`图示总动量为999` in the
stem and `图示P=999` in the explanation), plus whitespace, natural language, units,
`总动量为0`, and a nonzero line claimed through the origin.

## Verification and fresh audit

```text
python -m unittest tests.test_question_source_c -q
Ran 42 tests in 18.292s ... OK

Three C checkpoints: 3 tests ... OK (66 / 66 / 48)
Test-Json C source schema: True

C expansion/formal schema, manifest rejection, A byte parity, B generator parity,
A/B formal strictness, and C diagram determinism: 6 tests ... OK

AUDIT total=180 safe_questions=18 safe_claims=36
AUDIT safe_modes={'stem_figure': 9, 'text_only': 4, 'figure_sequence': 5}
AUDIT p_bearing_stem_or_explanation=19 momentum_stem_figures=7 stem_figures=72
AUDIT safe_visible_ratio_and_contract_binding=True momentum_symbolic_and_natural_language_binding=True

python -m unittest discover -s tests -q
Ran 156 tests in 30.650s ... OK
```

No question, diagram, schema, generator, or A/B asset changed in this round. The worktree is
clean after committing the test/semantic-validator changes.

## Concerns

None.

---

# Fix round 9 — Chinese ratio, momentum, and origin-proposition parsing

## Repairs

- Extended the student-visible mass-ratio parser with the `M:m=a:b` family,
  including ASCII/Chinese colons, mixed colon glyphs, spaces, and full-width
  equals. Existing slash, separate-assignment, and “4m与m” forms remain valid.
  Conflicting ratios are ambiguous, while zero, negative, malformed, and
  missing ratios fail the safe-sector contract.
- Extended numeric momentum parsing in both stem and explanation to accept
  ASCII/full-width equals and “总动量为/是” phrasing with optional spaces,
  punctuation, and units. The symbolic parser excludes identifiers such as
  `ΔP=...`, and question-like prose such as “总动量是否为...” is not treated as
  an asserted momentum value.
- Replaced the origin substring check with a polarity classifier for
  `通过/穿过/经过原点` and explicit negations. Nonzero-only figures reject
  positive origin claims; zero-only figures reject negative claims; mixed
  zero/nonzero figures reject generic origin claims as ambiguous. The double
  negation “不是不通过原点” is deliberately rejected rather than guessed.

## TDD evidence

RED before the mass-ratio and momentum parser changes:

```text
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_safe_sector_contract_masses_are_bound_to_the_visible_ratio tests.test_question_source_c.QuestionSourceCTests.test_momentum_statements_in_stem_and_explanation_match_the_figure -v

Ran 2 tests in 0.014s
FAILED (failures=2)
- M:m=16:1 conflict was accepted
- P＝999 was accepted
```

RED before the origin proposition classifier:

```text
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_origin_propositions_respect_crossing_and_negation_semantics -v

Ran 1 test in 0.011s
FAILED (failures=5)
- 穿过原点 and 经过原点 were accepted on a nonzero line
- 并非通过原点 and 不会通过原点 were rejected on a nonzero line
- 不是不通过原点 was accepted instead of rejected as ambiguous
```

GREEN:

```text
python -m unittest tests.test_question_source_c.QuestionSourceCTests.test_safe_sector_contract_masses_are_bound_to_the_visible_ratio tests.test_question_source_c.QuestionSourceCTests.test_momentum_statements_in_stem_and_explanation_match_the_figure tests.test_question_source_c.QuestionSourceCTests.test_origin_propositions_respect_crossing_and_negation_semantics -v
Ran 3 tests in 0.018s ... OK

python -m unittest tests.test_question_source_c -q
Ran 43 tests in 17.909s ... OK
```

## Verification and fresh audit

```text
Three C checkpoints: 3 tests ... OK (66 / 66 / 48)
Test-Json C source schema: True

C expansion/formal schema, manifest rejection, A byte parity, B generator
parity, A/B formal strictness, and C diagram determinism: 6 tests ... OK

AUDIT safe_sector_questions=18 p_bearing_records=19
AUDIT momentum_stem_figures=7 stem_figures=72
AUDIT all_safe_ratios_and_all_stem_figures_compatible=True

python -m unittest discover -s tests -q
Ran 157 tests in 30.892s ... OK
```

No question, diagram, schema, generator, or A/B asset changed in this round.

## Concerns

None.

---

# Fix round 10 final verification addendum

The full round-10 implementation, RED/GREEN evidence, architecture, and audit are
recorded above under “Fix round 10 — closed structured visible-physics facts”.
Final fresh verification after removing the prose parsers from correctness paths:

```text
python -m unittest tests.test_question_source_c -q
Ran 48 tests ... OK

python -m unittest discover -s tests -q
Ran 162 tests ... OK

AUDIT total=180 safe=18 numeric_momentum=19 momentum_stem_figures=7
AUDIT stem_figures=72 structured_claims=624 canonical_contracts=38
```

## Concerns

None.

---

# Round 10 completion — authoritative momentum and scenario context

Completed against base `23820f7`. Every numeric momentum fact now has a closed
scope: a specific line index in the bound diagram, the question's calculation
fixture, or the separately defined line through the origin. Diagram scopes read
`diagram-source-c.json` directly. Momentum-line calculations recompute
`sqrt(M)*x + sqrt(m)*y`; line-circle calculations use the fixture's momentum
input. No fixture `expected` value is used as an oracle. The origin-line scope
uses the identity `sqrt(M)*0 + sqrt(m)*0 = 0`, independently of its rendered prose.

Repeated references to a diagram line resolve to the same line index. The
parallel-line questions retain distinct P=2 and P=4 scopes; the explanation's
additional P=4 chord reference binds only that line. This avoids equating
unrelated prompt/explanation value sets.

All 27 controlled scenario questions carry a required `context_snapshot`.
Production checks it against scenario context before expansion and expansion
prefixes the stored snapshot deterministically. Both source and bank schemas
retain recursive closure; standalone contracts remain supported.

RED: the new production-path regression test failed all five subcases on the
base implementation: both diagram facts changed to 999 and rerendered, one
fact changed, line-calculation fact changed, intersection-calculation fact
changed, and the context-only appended contradiction.

GREEN:

```text
python -m unittest tests.test_question_source_c -q
Ran 49 tests in 58.637s ... OK

Three new focused production regression tests (including fixture-input drift
with expected answers untouched, and schema-required context snapshot):
Ran 3 tests in 2.994s ... OK

python -m unittest discover -s tests -q
Ran 165 tests in 53.669s ... OK
```

The final suite includes source/formal schema validation, all 38 controlled
expanded roundtrips, A/B parity, distributions, and accessibility checks.
An independent structural comparison to base confirmed that removing only
the newly added scopes and context snapshots restores the exact original
source JSON: all 180 questions and visible content are unchanged. Audit:
19 numeric-momentum records, 32 scoped facts (9 origin, 19 diagram, 4 fixture),
27 context snapshots. `git diff --check` passed. The untracked `docs/qa` port
report was preserved and is excluded from this commit.

## Concerns

None within the requested boundary. Deliberate edits to canonical templates,
scope assignments, and context snapshots remain author-controlled content
changes requiring review; this implementation does not interpret arbitrary prose.
