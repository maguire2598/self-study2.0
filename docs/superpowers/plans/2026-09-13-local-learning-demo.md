# SelfStudy Local Learning Demo Implementation Plan

> Agentic workers: use subagent-driven-development for the bounded backend, frontend and review work. User requested implementation and speed; proceed with this local-demo design without repeating approval prompts.

**Goal:** SQLite 数据库、A/B/C 488题学习及作者 demo，D待定。
**Architecture:** one loopback Python service, versioned SQLite, whitelist student DTO, cookie-isolated attempts, authenticated author APIs, vanilla frontend.
**Tech Stack:** Python stdlib / sqlite3 / HTTPServer / HTML / CSS / JavaScript.
**Spec:** docs/superpowers/specs/2026-09-13-local-learning-demo-design.md

**执行状态（2026-09-13）:** Task1/2功能与Task3运行验收已完成，详见 [验收记录](../../qa/local-demo-acceptance.md)。独立审核因额度限制未完成，不宣称审核通过；主控已检查具体风险并完成174项Python测试、3项前端测试和实际浏览器验收。以下保留原始任务清单，完成状态以验收记录为准。

## Global constraints

- A=140, B=168, C=180, D=0. 136 existing knowledge nodes. Preserve original question content.
- No answers/explanations/contracts in student DTO/static files. No status-observation questions or psychological inference.
- Loopback only, no public hosting/payments/real AI; rule followup clearly labeled.
- Idempotent import must preserve progress and author changes; test in temporary DB.
- Work in the already isolated collision-pi-c-question-bank worktree; main is not modified.

## Task 1: Database, C bank, backend and API verification

Files: demo/__init__.py, demo/database.py, demo/grading.py, demo/server.py, scripts/run_demo.py, scripts/generate_collision_pi_c_questions.py, content/courses/collision-pi/question-bank-c.json, tests/test_demo_backend.py, .gitignore.

Interfaces: `python scripts/run_demo.py --port 8765 --db .local/selfstudy-demo.sqlite3`; all API payloads and path names in spec are binding. `demo.server.create_server(host,port,db_path)` returns HTTP server for ephemeral integration tests; bootstraps db if necessary. Runtime token stored alongside DB as author-token.txt. DB module exports `initialize(db_path)` and `connect(db_path)` for tests. Student/static API route owns filesystem allowlist, not SimpleHTTPRequestHandler repository exposure.

- [ ] Write temporary-DB tests for counts, idempotence, enabled preservation and foreign keys; `initialize(path); initialize(path)` must still return488.
- [ ] Add public DTO/leakage and grade tests for single/multiple/blank including invalid shapes, duplicate IDs, nonfinite input, and request-size errors.
- [ ] Build C via existing validated shared builder, carry manifest fingerprint, write deterministic bank; seed database transactionally and persist protected answers separately.
- [ ] Implement API routes exactly as spec; opaque sessions and author login; filter/order/pagination; attempts, progress, reflections, author toggles and audit.
- [ ] Test actual HTTP on ephemeral loopback: two cookie jars, author401/login/409, restart progress, static traversal and private source404. No real user data touched.
- [ ] Run focused backend suite, existing full suite once, append report `docs/qa/demo-backend-report.md`, commit scoped files.

## Task 2: Learning and author frontend

Files: demo/web/index.html, app.js, styles.css, author.html, author.js; docs/product/demo-design.md. Consumes exact APIs above, no embedded bank or answer imports.

- [ ] Read spec/API routes. Build warm-paper workbench and responsive layout, semantic forms, keyboard support and visible focus.
- [ ] Fetch course/progress/questions; implement A/B/C/D, node/type filters, question navigation and all three answer shapes; preserve last question on refresh.
- [ ] Implement C stem/option/sequence figures via `/api/diagrams/`; neutral option accessibility; safe textContent for data.
- [ ] Submit once, show non-answer feedback and finite rule-reflection, save attempts, retry/skip and progress refresh.
- [ ] Author token login, filters/pagination, answer/analysis display only after authorized API response, enabled/revision toggle and logout.
- [ ] Check JS syntax and browser desktop/375px flows; write report and commit scoped files.

## Task 3: Acceptance, docs and running demo

- [ ] Independent scoped review backend security/data invariants and frontend flow; fix concrete findings.
- [ ] Start localhost service hidden, verify health488, database tables/counts and D0, actual browser submissions and reload, mobile overflow, C diagrams, author toggle restoration.
- [ ] Update README with one-command run, database/token paths, endpoint links and demo boundaries; update current decisions/roadmap without erasing history.
- [ ] Save final QA evidence, run relevant tests after amendments, report URL/DB/design plan. Keep server running for user. No main merge or cloud deployment.
