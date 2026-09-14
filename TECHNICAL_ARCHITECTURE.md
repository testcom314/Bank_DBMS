## Additional practical risks and recommended order for fixes

For educational purposes only - this project is deliberately simplified as a learning tool and a starting template for 12th‑grade projects. If you choose to improve or reuse the code, the list below names practical problems and gives a suggested order to begin fixing them.

Problems
- Authentication & session model: admin credentials are hard-coded and the app uses a global `current_acc` with no session timeout or role checks.
- Secrets in source: database credentials live in `config.py` instead of environment variables or a secrets store.
- PINs and passwords stored in plain text: secrets are directly readable from the database.
- No brute-force protection or account lockout: repeated bad PIN attempts are not rate-limited.
- Transaction safety and rollback: multi-step operations (transfers) commit without explicit rollback handling on unexpected errors.
- Monetary representation uses floats: using float can cause rounding errors in balances.
- Account-number generation race: `generate_account_number()` checks the DB then inserts, which can race under concurrency.
- No confirmation or audit for destructive actions: deletes are immediate and leave no audit trail.
- No automated tests or seed data: makes repeatable demos and regression checks harder.
- Blocking GUI calls: long database operations run on the GUI thread and can freeze the interface.
- Validation only in the UI: business validation is in the GUI and can be bypassed; the data layer is not defensive.
- No transport security guidance: if the DB runs over a network, connections are not configured for TLS in the examples.
- No schema migration or backup guidance: changes to the DB schema are not managed or documented.
- Logging may include sensitive values: the project does not explicitly avoid logging PINs/passwords or secrets.
- Limited error handling: some database reads assume rows exist and can raise errors that are not handled gracefully.

Recommended order to start fixing (practical, prioritized)
1. Move secrets out of `config.py` - read DB credentials from environment variables or a `.env` loader.
2. Hash PINs and admin passwords with a secure algorithm (bcrypt or argon2) and stop storing plain text.
3. Add transaction safety and rollback: use connection context managers and ensure `conn.rollback()` on exceptions.
4. Replace floats with `Decimal` in Python and `DECIMAL`/fixed-point types in the database for money.
5. Add a confirmation step and basic audit logging for destructive admin actions (who/when/what).
6. Introduce basic automated tests and a small `seed_demo.sql` so demos are repeatable and changes can be validated.
7. Prevent GUI blocking: run slow DB operations in a background thread or worker and update the UI afterward.
8. Improve account-number generation to avoid races (use DB-side sequences/auto-increment/UUID or handle duplicate-key on insert).
9. Add brute-force protections / rate-limiting and optional account lockout for repeated failed logins.
10. Harden logging and error handling: avoid logging secrets, add friendly error messages, and handle missing rows defensively.
11. Add transport and deployment guidance: recommend TLS for remote DBs and document firewalling / local-only assumptions.
12. Add migration and backup guidance (or adopt a migration tool) so schema changes are safer to apply.

This list is intended as a practical roadmap: tackle the top items first to make the project safer and more robust while preserving its value as a learning tool and template for student projects.
