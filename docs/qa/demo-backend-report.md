# Local demo backend verification — 2026-09-13

Implemented Task 1 against the local-learning-demo design and API contract. No API deviations.

- Deterministic C formal bank: 180 questions, manifest SHA-256, recomputed canonical content fingerprint. Existing A/B bytes unchanged.
- Transactional SQLite initialization: 488 questions (A140/B168/C180/D0), 136 nodes, 36 diagrams, foreign keys and WAL. Reinitialization preserves attempts and author toggles.
- Explicit public question projection; protected source/answer records; conservative choice and multi-blank grading without eval or symbolic/unit conversion.
- Actual loopback HTTP tests cover all three question types, opaque learner isolation, service restart persistence, finite reflection, author authentication/logout, revision conflicts, enabled preservation, private path rejection, allowed SVG serving, Host/Origin/header/body-size checks.
- Learner cookie lasts one year with HttpOnly/SameSite=Strict; author cookie is session-only. Author sessions expire when the service restarts.
- Runtime: `python scripts/run_demo.py --port 8765 --db .local/selfstudy-demo.sqlite3`. Token is stored beside the database in `author-token.txt`; no token is printed or returned by student APIs.

Verification results:

- `python -m unittest discover -s tests -v`: **172 passed**, 97.305 seconds.
- Final focused rerun after input validation/fingerprint amendments: **7 passed**, 7.263 seconds.
- Generated C bank validates against the formal JSON schema.
- `git diff --check`: passed (only normal Windows line-ending notices).

The HTTP tests use temporary databases, ephemeral loopback ports and explicit proxy bypass, and close every server/database handle. Frontend/browser acceptance remains Task 2/3. Demo only: no production account recovery, session management, real AI, video player, payments or cloud hosting.
